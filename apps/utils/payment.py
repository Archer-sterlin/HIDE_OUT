import json

import requests


class PaymentHandler:
    def __init__(self, auth, ref_id):
        self.auth = auth
        self.ref_id = ref_id
        self.headers = {
            "content-type": "application/json",
            "Authorization": f"Bearer {self.auth}",
        }
        self.context = {}

    def get_bank(self):
        url = "https://api.paystack.co/bank"
        param = {"perPage": "100"}
        payload = requests.get(url, params=param, headers=self.headers)
        data = json.loads(payload.content)
        # print(data['data'])
        return data

    def verify_bank_by_paystack(self, account_number, sort_code):
        url = "https://api.paystack.co/bank/resolve"
        payload = {"account_number": account_number, "bank_code": sort_code}
        try:
            payload = requests.get(url, params=payload, headers=self.headers)
            data = json.loads(payload.content)
            if data["status"]:
                response = {
                    "status": True,
                    "account_number": data["data"]["account_number"],
                    "account_name": data["data"]["account_name"],
                    "bank_id": data["data"]["bank_id"],
                }
                return response
            else:
                response = {"status": False}
                return response
        except:
            response = {"status": False}
            return response

    def rave_verify_bin(self):
        url = f"https://api.flutterwave.com/v3/card-bins/{self.ref_id}"
        try:
            payload = requests.get(url, headers=self.headers, params={})
            data = json.loads(payload.content)
            print(data)
            if data["status"] == "success":
                response = {
                    "status": "success",
                    "issuing_country": data["data"]["issuing_country"],
                    "card_type": data["data"]["card_type"],
                    "issuer_info": data["data"]["issuer_info"],
                }
                return response
            else:
                response = {"status": "error"}
                return response
        except Exception as ex:
            response = {"status": "error"}
            return response

    def rave_verify(self):
        status = True
        counter = 1
        while status:
            url = f"https://api.flutterwave.com/v3/transactions/{self.ref_id}/verify"
            payload = requests.get(url, headers=self.headers, params={})
            data = json.loads(payload.content)
            if data["status"] == "success":
                try:
                    # payment = Transaction.objects.get(tr_ref=data['data']['tx_ref'])
                    payment = {}
                except Exception as ex:
                    payment = None
                if payment:
                    try:
                        if int(data["data"]["amount"]) == payment.amount:
                            payment.status = "paid"
                            payment.save()
                            status = False
                            break
                    except:
                        pass
            if counter == 3:
                status = False
                break
            counter = counter + 1

    def paystack_verify(self):
        url = f"https://api.paystack.co/transaction/verify/{self.ref_id}"
        self.headers.pop("content-type")
        self.headers.update({"Cache-Control": "no-cache"})
        counter = 1
        status = True
        while status:
            payload = requests.get(url, headers=self.headers)
            data = json.loads(payload.content)
            if data["status"]:
                try:
                    # payment = Transaction.objects.get(tr_ref=data['data']['reference'])
                    payment = {}
                except Exception as ex:
                    payment = None
                if payment:
                    print("success on paystack {}".format(counter))
                    try:
                        if (int(data["data"]["amount"]) / 100) == payment.amount:
                            payment.status = "paid"
                            payment.save()
                            status = False
                            break
                    except:
                        pass
            if counter == 3:
                status = False
                break
            counter = counter + 1

    def payment_verifier(self, which):
        if which == "paystack":
            url = f"https://api.paystack.co/transaction/verify/{self.ref_id}"
            self.headers.pop("content-type")
            self.headers.update({"Cache-Control": "no-cache"})
            counter = 1
            status = True
            while status:
                payload = requests.get(url, headers=self.headers)
                data = json.loads(payload.content)
                if data["status"]:
                    self.context["status"] = True
                    self.context["ref"] = data["data"]["reference"]
                    self.context["amount"] = int(data["data"]["amount"]) / 100
                    status = False
                else:
                    self.context["status"] = False
                if counter == 3:
                    self.context["status"] = False
                    status = False
                    break
                counter = counter + 1
        else:
            url = "https://api.flutterwave.com/v3/transactions/{self.ref_id}/verify"
            status = True
            counter = 1
            while status:
                payload = requests.get(url, headers=self.headers, params={})
                data = json.loads(payload.content)
                print(data)
                if data["status"] == "success":
                    self.context["status"] = True
                    self.context["ref"] = data["data"]["tx_ref"]
                    self.context["amount"] = int(data["data"]["amount"])
                    status = False
                else:
                    self.context["status"] = False
                if counter == 3:
                    self.context["status"] = False
                    status = False
                    break
                counter = counter + 1
            print(self.context)
        return self.context


def verify_pay(gateway, key, ref_id):
    if gateway == "rave":
        PaymentHandler(key, ref_id).rave_verify()
    else:
        PaymentHandler(key, ref_id).paystack_verify()
