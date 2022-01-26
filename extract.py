from bs4 import BeautifulSoup
import requests
import json


class Information:
    def __init__(self, url=None, headers=None):
        self.__information = {"url": url, "headers": headers}
        self.__data = {}
        self.__request = requests.Session()
        self.__token = self.set_token()

    def get_information(self, method="get"):
        if method == "get":
            response = self.__request.get(
                self.__information["url"], headers=self.__information["headers"]
            )
        else:
            response = self.__request.post(
                self.__information["url"], data=self.__information["headers"]
            )

        page = BeautifulSoup(response.content, "html.parser")
        return page

    def set_contacts(self, soup):
        table = soup.find("div", {"class": "col-md-3"})
        text = table.text.split("\n")
        self.__data = {
            "email": text[1].split(":")[1],
            "telefones": text[2].split(":")[1],
            "Endereco": text[3].split(":")[1],
            "Cidade": text[4].split(":")[1],
        }

    def set_debits(self, soup):
        values = soup.find_all("input", {"name": "ano_parcela"})

        for value in values:
            headers = {
                "ano_parcela": value.get("value"),
                "_token": self.__token,
                "Content-Type": "application/x-www-form-urlencoded",
            }
            self.set_headers(headers)
            response = self.get_information("post")
            debit = response.find("table", {"class": "table"}).text.split("\n")
            self.__data[value.get("value")] = {
                "ano": value.get("value").split("_")[0],
                "parcela": value.get("value").split("_")[1],
                "vencimento": debit[10],
                "valor": debit[11],
            }

    def set_headers(self, headers):
        self.__information["headers"] = headers

    def set_url(self, url):
        self.__information["url"] = url

    def set_token(self):
        page = self.get_information()
        return page.find("input", {"name": "_token"}).get("value")

    def start(self):
        soup = self.get_information()
        self.set_contacts(soup)
        self.set_url("https://sistema.scod.com.br/teste_detalhes")
        self.set_debits(soup)
        print(json.dumps(self.__data))
