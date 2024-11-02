from app.services.logs.logging import logger


def create_text(account_type: str, acc_info: list, counters: list):
    try:
        projects_counter, companies_counter, managers_counter = counters
        if account_type == "users":
            msg_text = (f"Роль: {acc_info[3]}\n"
                        f"Username: @{acc_info[2]}\n"
                        f"Chat_id: {acc_info[1]}\n")
            if acc_info[3] == "team-lead":
                msg_text += f"Кол-во менеджеров: {managers_counter}\n"
            msg_text += (f"Кол-во проектов: {projects_counter}\n"
                         f"Кол-во компаний: {companies_counter}")
        else:
            if acc_info[1] == "posts":
                task = "Секретарь для постов"
            elif acc_info[1] == "agent":
                task = "Аккаунт-агент"
            else:
                task = "Секретарь для комментариев"

            msg_text = (f"Роль: {task}\n"
                        f"Имя: {acc_info[7]}\n"
                        f"Username: @{acc_info[8]}\n"
                        f"Наличие прокси: {acc_info[2] if acc_info[2] else "Нет"}")
        return msg_text
    except Exception as e:
        logger.error("Возникла ошибка в create_text: %s", e)
