from wafl.scheduler.web_interface_implementation import get_html_from_dialogue_item


class MessagesCreator:
    def __init__(self, interface):
        self._interface = interface
        self._toggled_windows = []

    def toggle_logs(self):
        if "logs" in self._toggled_windows:
            self._toggled_windows.remove("logs")
        else:
            self._toggled_windows.append("logs")

    async def get_messages_window(self):
        conversation = ""
        conversation += await self._get_dialogue()
        if "logs" in self._toggled_windows:
            conversation += await self._get_logs()

        return conversation

    async def _get_dialogue(self):
        dialogue_items = self._interface.get_utterances_list()
        dialogue_items = [
            get_html_from_dialogue_item(item) for item in dialogue_items[::-1]
        ]
        conversation = (
            "<div id='dialogue' class='dialogue overflow-y-scroll rounded-lg'>"
        )
        conversation += "".join(dialogue_items)
        return conversation

    async def _get_logs(self):
        choices = self._interface.get_choices_and_timestamp()
        choices = [
            (
                item[0],
                "<div class='log-row'>" + item[1] + "</div>",
            )
            for item in choices
        ]
        facts = self._interface.get_facts_and_timestamp()
        facts = [
            (
                item[0],
                "<div class='log-row'>" + item[1] + "</div>",
            )
            for item in facts
        ]

        choices_and_facts = choices + facts
        choices_and_facts = sorted(choices_and_facts, key=lambda x: x[0])[::-1]
        choices_and_facts = [item[1] for item in choices_and_facts]
        conversation = "</div>"
        conversation += "<div id='logs' class='logs shadow-lg overflow-y-scroll rounded-lg width' style='flex-direction: column-reverse;'>"
        conversation += "".join(choices_and_facts)
        conversation += "</div>"
        return conversation
