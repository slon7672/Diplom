import os
from Pages.API_YGP import ProjectYouGile
from dotenv import load_dotenv


load_dotenv()
client = ProjectYouGile()


# def test_get_api_keys():
#     """
#     Получает ID Вашей компании, Ваш API-key и Ваш user_ID
#     через API запросы.
#     Returns:
#     Dict[str, Any]: словари с данными
#     (содержат поля "id").
#     """
#     log: str = os.getenv("LOG")
#     password: str = os.getenv("PASS")
#
#     stat, resp = client.get_id_company(log, password)
#     assert stat == 200
#     company = resp["content"][0]
#     company_id: str = company["id"]
#
#     status, response = client.get_api_key(log, password, company_id)
#     assert status == 201
#     api_key: str = response["key"]
#
#     status_code, response_body = client.get_all_users(api_key)
#     assert status_code == 200
#     users = response_body["content"][0]
#     user: str = users["id"]
#
#     print(f'ID Вашей компании : {company_id}')
#     print(f'Ваш API-key : {api_key}')
#     print(f'Ваш user_ID : {user}')