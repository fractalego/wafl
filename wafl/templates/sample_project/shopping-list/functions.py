import json

from fuzzywuzzy import process


def get_shopping_list_in_english():
    shopping_list = json.load(open("shopping_list.json"))
    if not shopping_list:
        return "Nothing"

    return ", ".join(shopping_list)


def add_shopping_list(item):
    if "shopping" in item.lower():
        return False

    if "add " in item.lower():
        item = item.lower().replace("add ", "")

    if not {
        f"% The user adds {item} to a list :- the user adds something to a grocery list %"
    }:
        if not {f"% Do you really want to add {item}?%"}:
            return False

    shopping_list = json.load(open("shopping_list.json"))
    if " and " in item:
        items_to_add = item.split(" and ")
        shopping_list.extend(items_to_add)

    else:
        shopping_list.append(item)

    json.dump(shopping_list, open("shopping_list.json", "w"))
    f"% SAY {item} has been added to the shopping list%"
    return True


def remove_from_shopping_list(item):
    shopping_list = json.load(open("shopping_list.json"))
    if not shopping_list:
        "% SAY the shopping list is already empty.%"
        return False

    extracted, score = process.extract(item, shopping_list, limit=1)[0]
    if score < 60:
        f"% SAY I did not quite get the item to remove %"
        return False

    if not {f"% Do you want to remove {extracted} from the shopping list? %"}:
        return False

    shopping_list.remove(extracted)
    json.dump(shopping_list, open("shopping_list.json", "w"))
    return True


def remove_first_item_from_shopping_list():
    shopping_list = json.load(open("shopping_list.json"))
    if not shopping_list:
        "% SAY the shopping list is already empty.%"
        return False

    shopping_list.pop(0)
    json.dump(shopping_list, open("shopping_list.json", "w"))
    return True


def remove_last_item_from_shopping_list():
    shopping_list = json.load(open("shopping_list.json"))
    if not shopping_list:
        "% SAY the shopping list is already empty.%"
        return False

    shopping_list.pop(-1)
    json.dump(shopping_list, open("shopping_list.json", "w"))
    return True


def reset_shopping_list():
    shopping_list = []
    json.dump(shopping_list, open("shopping_list.json", "w"))
    return True
