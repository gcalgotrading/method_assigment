from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import xmltodict
import json
import requests
from method import Method
from method.errors import MethodInvalidRequestError
from .models import Entity, Account, Payment
method = Method(env="dev", api_key="sk_YfGKwBCX6BFd9wKn8CfEKnQa")


# 1. Total amount of funds paid out per unique source account.
    # find all payments attached to each source
# 2. Total amount of funds paid out per Dunkin branch.
# 3. The status of every payment and its relevant metadata.
@csrf_exempt
def dashboard_view(request):
    if request.method == "POST" and request.FILES.get("xml_file"):
        xml_file = request.FILES["xml_file"]
        xml_dict = xmltodict.parse(xml_file)
        rows = xml_dict["root"]["row"]

        entities_list = []
        dunkin_ids_list = []
        for row in rows:
            individual_data, corporate_data, employee_dunkin_id, payor_dunkin_id = process_row(row)
            entities_list.append(individual_data)
            entities_list.append(corporate_data)
            dunkin_ids_list.append((employee_dunkin_id, payor_dunkin_id))

        created_entities_response = []

        for entity_data, dunkin_ids in zip(entities_list, dunkin_ids_list):
            if entity_data['type'] == 'individual':
                first_name = entity_data['individual']['first_name']
                last_name = entity_data['individual']['last_name']
                existing_entity = Entity.objects.filter(type='individual', first_name=first_name, last_name=last_name).first()
            elif entity_data['type'] == 'c_corporation':
                ein = entity_data['corporation']['ein']
                existing_entity = Entity.objects.filter(type='c_corporation', ein=ein).first()

            if not existing_entity:
                response = method.entities.create(entity_data)
                created_entities_response.append(response)
                if entity_data['type'] == 'individual':
                    entity = Entity(type='individual', entity_id=created_entities_response[-1]['id'], first_name=entity_data['individual']['first_name'], last_name=entity_data['individual']['last_name'], dunkin_id=dunkin_ids[0])
                elif entity_data['type'] == 'c_corporation':
                    entity = Entity(type='c_corporation', entity_id=created_entities_response[-1]['id'], ein=entity_data['corporation']['ein'], corporation_name=entity_data['corporation']['name'], dunkin_id=dunkin_ids[1])
                entity.save()

        existing_entities = json.dumps(list(Entity.objects.all().values()), indent=4)

        # Create accounts
        accounts = []
        for entity_data in created_entities_response:
            response = method.accounts.create(
                {
                    'holder_id': entity_data['id'],
                    'ach': {
                        'routing': '367537407',
                        'number': '57838927',
                        'type': 'checking'
                    }
                }
            )
            if response.get('id'):
                account = Account(
                    account_id=response['id'],
                    holder_id=response['holder_id'],   
                    entity=Entity.objects.get(entity_id=entity_data['id'])
                )
                account.save()
                accounts.append(account)

        payment_list = []
        for row in rows:
            payment_data = process_payment(row)
            payment_list.append(payment_data)
        return render(
            request,
            "payout_dashboard/dashboard.html",
            {
                "entities": existing_entities,
                "process_payments": True,
                "payments": payment_list
            },
        )
    elif request.method == "POST" and request.POST.getlist("payment_amounts[]"):
        payment_amounts = request.POST.getlist("payment_amounts[]")
        payment_sources = request.POST.getlist("payment_sources[]")
        payment_destinations = request.POST.getlist("payment_destinations[]")
        payment_descriptions = request.POST.getlist("payment_descriptions[]")
        for i in range(len(payment_amounts)):
            payment = {
                "amount": float(payment_amounts[i][1:]) * 100,
                "source": payment_sources[i],
                "destination": payment_destinations[i],
                "description": payment_descriptions[i],
            }
            try:
                response = method.payments.create(payment)
            except MethodInvalidRequestError as e:
                payment = Payment(
                    amount= float(payment_amounts[i][1:]) * 100,
                    source= payment_sources[i],
                    destination= payment_destinations[i],
                    description= payment_descriptions[i],
                )
                payment.save()

        return render(
            request,
            "payout_dashboard/dashboard.html",
            {
                "payments_authorized": True,
            },
        )
    return render(request, "payout_dashboard/dashboard.html")

def process_payment(row):
    amount = row["Amount"]
    destination_dunkin_id = row['Employee'].get("DunkinId") 
    source_dunkin_id = row['Payor'].get("DunkinId") 
    destination_account = Account.objects.filter(entity__dunkin_id=destination_dunkin_id).first()
    source_account = Account.objects.filter(entity__dunkin_id=source_dunkin_id).first()
    source_account_id = getattr(source_account, 'account_id', 'default_source_account_id')
    destination_account_id = getattr(destination_account, 'account_id', 'default_destination_account_id') 
    description = 'Loan Pmt'
    payment_data = {
        'amount': amount,
        'source': source_account_id,
        'destination': destination_account_id,
        'description': description,
    }

    return payment_data
def process_row(row):
    employee_data = row["Employee"]
    payor_data = row["Payor"]
    employee_dunkin_id = employee_data.get("DunkinId")
    payor_dunkin_id = payor_data.get("DunkinId")

    individual_data = {
        "type": "individual",
        "individual": {
            "first_name": employee_data["FirstName"],
            "last_name": employee_data["LastName"],
            "phone": "+15121231111",
        }
    }

    corporation_data = {
        "type": "c_corporation",
        "corporation": {
            "name": payor_data["Name"],
            "dba": payor_data["DBA"],
            "ein": payor_data["EIN"],
            "owners": [],
        },
        "address": {
            "line1": payor_data["Address"]["Line1"],
            "line2": None,
            "city": payor_data["Address"]["City"],
            # Not sure if this is a bug or not, does not work if I set state to Iowa and zip code to 94043
            "state": 'CA',
            "zip": '94043',
        }
    }

    return individual_data, corporation_data, employee_dunkin_id, payor_dunkin_id

def create_accounts(entities):
    return None
