"""
Todo AI Agent Configuration
Implements the AI agent that processes user requests using MCP tools
"""

from typing import Dict, Any, List, Optional, Tuple
import re

# Import using absolute paths from the backend directory
import sys
from pathlib import Path

# Add the backend directory to the Python path to resolve imports
backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from mcp_server.server import get_mcp_server


# Keywords that signal each intent. When several appear in one message,
# the one that appears first wins ("edit task 1 to add milk" is an edit).
INTENT_KEYWORDS = {
    "add_task": ["remind me to", "add", "create", "new", "put"],
    "list_tasks": ["show", "display", "list", "lists", "view", "open", "what do", "what's in", "what is in",
                   "tell me", "my tasks", "have to do"],
    "complete_task": ["complete", "done", "finish", "finished", "mark", "check off", "tick off", "reopen", "uncheck"],
    "update_task": ["update", "change", "modify", "edit", "rename"],
    "delete_task": ["delete", "remove", "get rid of", "cancel", "erase", "clear"],
    "help": ["help", "what can you do"],
}

ORDINALS = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5}

HELP_TEXT = (
    "Here's what I can do:\n"
    "Lists\n"
    "• \"Create a list called Groceries\" (or \"…with milk, eggs\")\n"
    "• \"Show my lists\" or \"Show Groceries\"\n"
    "• \"Rename the Groceries list to Shopping\"\n"
    "• \"Delete the Work list\"\n"
    "Items\n"
    "• \"Add milk, eggs and bread to Groceries\"\n"
    "• \"Add fruits in task 1\" (adds a sub-item under item 1)\n"
    "• \"Edit task 2 to buy oat milk\" or \"Edit task 1.1 to apples\"\n"
    "• \"Mark milk in Groceries as done\" (or \"as not done\")\n"
    "• \"Delete eggs from Groceries\", \"Delete task 3\" or \"Clear completed tasks\""
)

_LIST_SUFFIX = r"(?:\s+list)?"


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().strip("\"'").lower())


def _strip_quotes(text: str) -> str:
    return text.strip().strip(" .!?:").strip("\"'").strip()


def _split_items(text: str) -> List[str]:
    """'milk, eggs and bread' -> ['milk', 'eggs', 'bread']; no commas -> one item"""
    if "," not in text:
        return [text.strip()] if text.strip() else []
    parts = [p for p in re.split(r"\s*,\s*", text) if p.strip()]
    last = re.split(r"\s+and\s+", parts[-1])
    parts = parts[:-1] + last
    return [re.sub(r"^and\s+", "", p.strip(), flags=re.IGNORECASE) for p in parts if p.strip()]


class TodoAgent:
    def __init__(self):
        self.mcp_server = get_mcp_server()
        self.instructions = """
        You are an AI assistant for managing todos. You can help users create titled lists and
        add, list, update, complete, and delete the items in them.
        You MUST use the available tools to perform these actions. Under NO circumstances may you attempt to access data directly or perform operations outside the available tools.

        Available tools:
        1. add_task: Add a new task to one of the user's lists
        2. list_tasks / get_lists: Show the user's lists and tasks
        3. update_task: Modify an existing task
        4. complete_task: Mark a task as completed
        5. delete_task: Remove a task from a list
        6. create_list / rename_list / delete_list: Manage titled lists

        Always confirm actions with the user in a friendly way.
        If the user speaks Urdu, respond in Urdu.
        """

    async def process_request(self, user_input: str, user_id: str) -> str:
        """
        Process a user request and return an appropriate response
        """
        text = user_input.strip()

        lists, tasks, error = await self._load(user_id)
        if error:
            return error

        # List-level commands first: they are more specific than item commands
        list_response = await self._try_list_command(text, user_id, lists)
        if list_response:
            return list_response

        intent = self._analyze_intent(text)
        action = intent["action"]

        if action == "add_task":
            return await self._handle_add_task(intent, user_id, lists, tasks)
        elif action == "list_tasks":
            return self._handle_list_tasks(intent, lists, tasks)
        elif action == "update_task":
            return await self._handle_update_task(intent, user_id, lists, tasks)
        elif action == "complete_task":
            return await self._handle_complete_task(intent, user_id, lists, tasks)
        elif action == "delete_task":
            return await self._handle_delete_task(intent, user_id, lists, tasks)
        elif action == "help":
            return HELP_TEXT
        else:
            return "I'm not sure how to help with that.\n\n" + HELP_TEXT

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    async def _load(self, user_id: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Optional[str]]:
        """
        Load the user's lists, plus every task flattened in display order with a
        global "number" (1, 2, 3… across all lists) and its list's title.
        """
        result = await self.mcp_server.call_tool("get_lists", {"user_id": user_id})
        if not result["success"]:
            return [], [], f"Sorry, I couldn't load your lists: {result['message']}"

        lists = result["lists"]
        tasks = []
        top_number = 0
        for todo_list in lists:
            for task in todo_list["tasks"]:
                top_number += 1
                task["number"] = str(top_number)
                task["list_title"] = todo_list["title"]
                task["parent"] = None
                tasks.append(task)
                # Sub-items are numbered under their parent: 1.1, 1.2, …
                for k, subtask in enumerate(task.get("subtasks", []), 1):
                    subtask["number"] = f"{top_number}.{k}"
                    subtask["list_title"] = todo_list["title"]
                    subtask["parent"] = task
                    tasks.append(subtask)
        return lists, tasks, None

    def _find_list(self, name: str, lists: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Match a list by title, ignoring case, a leading "my/the" and a trailing "list" """
        name = re.sub(r"\s+list$", "", _norm(name))
        candidates = {name, re.sub(r"^(my|the)\s+", "", name)}
        for todo_list in lists:
            if _norm(todo_list["title"]) in candidates:
                return todo_list
        return None

    def _find_parent(self, name: str, tasks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Match an item by number ("task 1", "tasks 1", "#1") or exact top-level name.
        "task 1.1" returns that sub-item, so callers can explain it can't nest further.
        """
        ref = self._clean_ref(name)
        top_level = [t for t in tasks if not t.get("parent")]
        number = re.fullmatch(r"(?:(?:tasks?|todos?|items?)\s*)?(?:number\s*|no\.?\s*)?#?(\d+(?:\.\d+)?)", ref, re.IGNORECASE)
        if number:
            return next((t for t in tasks if t["number"] == number.group(1)), None)
        ref = re.sub(r"^(?:tasks?|todos?|items?)\s+", "", ref, flags=re.IGNORECASE) if not any(
            _norm(t["description"]) == _norm(ref) for t in top_level) else ref
        return next((t for t in top_level if _norm(t["description"]) == _norm(ref)), None)

    def _describe(self, task: Dict[str, Any]) -> str:
        """'"fruits" (under "milk")' for sub-items, '"milk"' for items"""
        if task.get("parent"):
            return f"\"{task['description']}\" (under \"{task['parent']['description']}\")"
        return f"\"{task['description']}\""

    # ------------------------------------------------------------------
    # List-level commands
    # ------------------------------------------------------------------

    async def _try_list_command(self, text: str, user_id: str, lists: List[Dict[str, Any]]) -> Optional[str]:
        create = re.match(
            r"^(?:please\s+)?(?:create|make|start|add|new)\s+(?:a\s+)?(?:new\s+)?list\b"
            r"(?:\s+(?:called|named|titled|for))?\s*:?\s*(.*)$",
            text, re.IGNORECASE
        )
        if create:
            return await self._create_list(create.group(1), user_id)

        delete = re.match(
            r"^(?:please\s+)?(?:delete|remove|erase)\s+(?:the\s+)?(?:(?:whole|entire)\s+)?"
            r"(?:list\s+(?:called\s+|named\s+)?(.+)|(.+?)\s+list)\s*[.!]?$",
            text, re.IGNORECASE
        )
        if delete:
            todo_list = self._find_list(delete.group(1) or delete.group(2), lists)
            if todo_list:
                result = await self.mcp_server.call_tool(
                    "delete_list", {"user_id": user_id, "list_id": todo_list["id"]}
                )
                return result["message"] + (" 🗑️" if result["success"] else "")

        rename = re.match(
            r"^(?:please\s+)?(?:rename|change|edit|update)\s+(?:the\s+)?(?:(?:title|name)\s+of\s+(?:the\s+)?)?"
            r"(?:list\s+(.+?)|(.+?)\s+list)\s+(?:to|into|as)\s+(.+)$",
            text, re.IGNORECASE
        )
        if rename:
            todo_list = self._find_list(rename.group(1) or rename.group(2), lists)
            if todo_list:
                return await self._rename_list(todo_list, rename.group(3), user_id)

        return None

    async def _create_list(self, rest: str, user_id: str) -> str:
        title, items = rest, []
        with_items = re.match(r"^(.*?)\s+(?:with|containing)\s+(.+)$", rest, re.IGNORECASE)
        if with_items:
            title, items = with_items.group(1), _split_items(_strip_quotes(with_items.group(2)))
        title = _strip_quotes(title)
        if not title:
            return "What should the list be called? Try \"Create a list called Groceries\"."

        result = await self.mcp_server.call_tool("create_list", {"user_id": user_id, "title": title})
        if not result["success"]:
            return f"Sorry, {result['message'][0].lower()}{result['message'][1:]}"

        response = f"Created the list \"{title}\". 🗂️"
        added = []
        for item in items:
            item_result = await self.mcp_server.call_tool(
                "add_task", {"user_id": user_id, "task_description": item, "list_id": result["list_id"]}
            )
            if item_result["success"]:
                added.append(item)
        if added:
            response += "\nAdded: " + ", ".join(added) + "."
        else:
            response += f"\nAdd items with \"Add milk to {title}\"."
        return response

    async def _rename_list(self, todo_list: Dict[str, Any], new_title: str, user_id: str) -> str:
        new_title = _strip_quotes(new_title)
        new_title = re.sub(r"\s+list$", "", new_title, flags=re.IGNORECASE)
        if not new_title:
            return "What should the new title be?"
        result = await self.mcp_server.call_tool(
            "rename_list", {"user_id": user_id, "list_id": todo_list["id"], "title": new_title}
        )
        if result["success"]:
            return f"Renamed the list \"{todo_list['title']}\" to \"{new_title}\". ✏️"
        return f"Sorry, I couldn't rename that list: {result['message']}"

    # ------------------------------------------------------------------
    # Intent analysis
    # ------------------------------------------------------------------

    def _analyze_intent(self, text: str) -> Dict[str, Any]:
        """
        Analyze the user's input to determine the intended action
        """
        # Find the earliest keyword; prefer the longer keyword on a tie
        best: Optional[Tuple[int, int, str, re.Match]] = None
        for action, keywords in INTENT_KEYWORDS.items():
            for keyword in keywords:
                match = re.search(r"\b" + re.escape(keyword) + r"\b", text, re.IGNORECASE)
                if match:
                    candidate = (match.start(), -len(keyword), action, match)
                    if best is None or candidate[:2] < best[:2]:
                        best = candidate

        if best is None:
            return {"action": "unknown"}

        action, match = best[2], best[3]
        rest = text[match.end():].strip()

        if action == "add_task":
            return {"action": action, "description": self._extract_add_description(rest)}
        if action == "list_tasks":
            return {"action": action, "status_filter": self._extract_status_filter(text), "rest": rest}
        if action == "complete_task":
            return {
                "action": action,
                "task_ref": self._extract_complete_ref(text),
                "reopen": bool(re.search(r"\b(not done|not complete[d]?|incomplete|undone|reopen|uncheck)\b", text, re.IGNORECASE)),
            }
        if action == "update_task":
            return {"action": action, "rest": rest}
        if action == "delete_task":
            return {"action": action, "task_ref": rest}
        return {"action": action}

    def _extract_add_description(self, rest: str) -> str:
        # Drop leading filler like "a task", "task:", "to my list:", "to"
        description = re.sub(
            r"^((to|on)\s+(my|the)\s+(todo\s+|task\s+)?list\s*:?\s*)?(a\s+)?(new\s+)?((task|todo|item)s?\b)?\s*:?\s*(to\s+)?",
            "", rest, flags=re.IGNORECASE
        )
        # Drop trailing phrases like "to my list" / "to the todo list"
        description = re.sub(
            r"\s*(to|on|in)\s+(my|the)\s+(todo\s+|task\s+)?list\s*[.!]?$", "", description, flags=re.IGNORECASE
        )
        return description.strip(" .!:\"'")

    def _extract_status_filter(self, text: str) -> Optional[str]:
        lowered = text.lower()
        if re.search(r"\b(incomplete|pending|active|remaining|not done|unfinished)\b", lowered):
            return "incomplete"
        if re.search(r"\b(completed|done|finished)\b", lowered):
            return "completed"
        return None

    def _extract_complete_ref(self, text: str) -> str:
        patterns = [
            r"\bmark(?:ed)?\s+(.+?)\s+as\s+(?:not\s+)?(?:done|complete[d]?|finished|incomplete|undone)\b",
            r"\b(?:complete|finish|finished|check off|tick off|reopen|uncheck)\s+(.+)$",
            r"^(?:i\s+)?(?:have\s+|i've\s+)?(.+?)\s+(?:is\s+)?(?:done|completed|finished)\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""

    # ------------------------------------------------------------------
    # Task resolution
    # ------------------------------------------------------------------

    def _clean_ref(self, ref: str) -> str:
        ref = ref.strip(" .!?\"'")
        ref = re.sub(r"\s+(from|on|in|off)\s+(my|the)\s+(todo\s+|task\s+)?list$", "", ref, flags=re.IGNORECASE)
        ref = re.sub(r"^(the\s+)?(description|name|title|text)\s+of\s+", "", ref, flags=re.IGNORECASE)
        ref = re.sub(r"^(my|the|a)\s+", "", ref, flags=re.IGNORECASE)
        ref = re.sub(r"\s+(task|todo|item)$", "", ref, flags=re.IGNORECASE)
        return ref.strip(" .!?\"'")

    def _scope_ref(
        self, raw_ref: str, lists: List[Dict[str, Any]], tasks: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]], Optional[str]]:
        """
        Narrow a reference to a list or to an item's sub-items:
        'eggs from Groceries' -> ('eggs', items in Groceries, 'Groceries')
        'fruits in task 1'    -> ('fruits', sub-items of item 1, 'item 1 "milk"')
        """
        scoped = re.match(r"^(.+?)\s+(?:from|in|on|of|under|inside)\s+(.+)$", raw_ref.strip(), re.IGNORECASE)
        if scoped:
            todo_list = self._find_list(scoped.group(2), lists)
            if todo_list:
                return scoped.group(1), [t for t in tasks if t["list_id"] == todo_list["id"]], todo_list["title"]
            parent = self._find_parent(scoped.group(2), tasks)
            if parent:
                subtasks = [t for t in tasks if t.get("parent") is parent]
                return scoped.group(1), subtasks, f"item {parent['number']} \"{parent['description']}\""
        return raw_ref, tasks, None

    def _resolve_task(
        self, raw_ref: str, lists: List[Dict[str, Any]], tasks: List[Dict[str, Any]], exact_only: bool = False
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Find the task a user is referring to by number ("task 2", "#2",
        "second", "last"), by name, or by name within a list ("eggs from
        Groceries"). Returns (task, error_message). Never guesses: ambiguous
        or unknown references produce an error.
        """
        # An item whose whole name matches wins before any scoping ("fruits in tasks 1" as a name)
        whole = _norm(self._clean_ref(raw_ref))
        for task in tasks:
            if whole and _norm(task["description"]) == whole:
                return task, None

        raw_ref, candidates, scope = self._scope_ref(raw_ref, lists, tasks)
        ref = self._clean_ref(raw_ref)
        where = f" in {scope}" if scope else ""
        if not ref:
            return None, "Which item? Use its number (like \"task 2\" or \"task 1.2\") or part of its name."
        if not candidates:
            return None, f"There are no items{where} yet."

        # Numbers are labels: "3" for an item, "3.2" for its second sub-item
        label = None
        number_match = re.fullmatch(
            r"(?:(?:sub[- ]?)?(?:tasks?|todos?|items?)\s*)?(?:number\s*|no\.?\s*)?#?(\d+(?:\.\d+)?)", ref, re.IGNORECASE
        )
        top_level = [t for t in candidates if not t.get("parent")] or candidates
        if number_match:
            label = number_match.group(1)
        elif _norm(ref) in ORDINALS:
            position = ORDINALS[_norm(ref)]
            if position <= len(top_level):
                return top_level[position - 1], None
            return None, f"There's no {_norm(ref)} item{where}."
        elif _norm(ref) in ("last", "latest", "newest"):
            return top_level[-1], None

        if label is not None:
            for task in candidates:
                if task["number"] == label:
                    return task, None
            # Within a list or item, also accept the position there ("item 2 in Groceries")
            if scope and label.isdigit() and 1 <= int(label) <= len(candidates):
                return candidates[int(label) - 1], None
            return None, f"There's no item {label}{where}. Say \"show my lists\" to see the numbers."

        target = _norm(ref)
        exact = [t for t in candidates if _norm(t["description"]) == target]
        if exact:
            return exact[0], None
        if exact_only:
            return None, None

        partial = [t for t in candidates if target in _norm(t["description"])]
        if len(partial) == 1:
            return partial[0], None
        if len(partial) > 1:
            options = "\n".join(f"{t['number']}. {t['description']} ({t['list_title']})" for t in partial)
            return None, f"I found several items matching \"{ref}\":\n{options}\nWhich one? Use its number, e.g. \"task {partial[0]['number']}\"."
        return None, f"I couldn't find an item matching \"{ref}\"{where}. Say \"show my lists\" to see everything."

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _find_add_parent(self, description: str, tasks: List[Dict[str, Any]]) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Detect a sub-item request and return (text to add, parent item):
        "fruits in task 1", "fruits in tasks 1", "apples under milk", "fruits to task milk".
        A plain "go to gym" stays a normal item: a parent named without a number
        needs "under/inside/below" or the word "task".
        """
        match = re.match(
            r"^(.*\S)\s+(to|in|on|into|under|inside|below|beneath)\s+(?:the\s+)?(.+)$", description, re.IGNORECASE
        )
        if not match:
            return description, None
        text, preposition, ref = match.group(1), match.group(2).lower(), match.group(3)
        sub_item_words = re.sub(r"\s+as\s+(?:a\s+)?sub[- ]?(?:items?|tasks?)$", "", text, flags=re.IGNORECASE)

        numbered = re.fullmatch(r"(?:tasks?|todos?|items?)\s*#?\d+(?:\.\d+)?|#\d+(?:\.\d+)?", ref.strip(), re.IGNORECASE)
        named_task = re.match(r"^(?:tasks?|todos?|items?)\s+\D", ref.strip(), re.IGNORECASE)
        if numbered or named_task or preposition in ("under", "inside", "below", "beneath"):
            parent = self._find_parent(ref, tasks)
            if parent:
                return sub_item_words, parent
        return description, None

    async def _handle_add_task(
        self, intent: Dict[str, Any], user_id: str, lists: List[Dict[str, Any]], tasks: List[Dict[str, Any]]
    ) -> str:
        """
        Handle adding one or more items, optionally to a named list or under an item:
        "add milk", "add milk to Groceries", "add milk, eggs and bread to my groceries list",
        "add fruits in task 1", "add apples, pears under milk potatos"
        """
        description = intent.get("description", "")
        if not description:
            return "Please tell me what to add, e.g. \"Add milk to Groceries\"."

        target = None
        # The list name keeps a leading "my/the" so a list titled "My tasks" still matches
        to_list = re.match(r"^(.*\S)\s+(?:to|in|on|into|under)\s+(.+?)(\s+list)?$", description, re.IGNORECASE)
        if to_list:
            target = self._find_list(to_list.group(2), lists)
            if target:
                description = to_list.group(1)
            elif to_list.group(3):
                name = re.sub(r"^(my|the)\s+", "", _strip_quotes(to_list.group(2)), flags=re.IGNORECASE)
                return f"You don't have a list called \"{name}\". Create it first with \"Create a list called {name}\"."

        parent = None
        if not target:
            description, parent = self._find_add_parent(description, tasks)
            if parent and parent.get("parent"):
                return (
                    f"Item {parent['number']} is already a sub-item, so it can't have its own. "
                    f"Add it under item {parent['parent']['number']} instead."
                )
        if not parent and re.search(r"\b(?:in|to|under|into)\s+(?:tasks?|items?)\s*#?\d+(?:\.\d+)?\s*$", description, re.IGNORECASE):
            number = re.search(r"(\d+(?:\.\d+)?)\s*$", description).group(1)
            return f"There's no item {number}. Say \"show my lists\" to see the numbers."

        items = _split_items(description)
        if not items:
            return "Please tell me what to add, e.g. \"Add milk to Groceries\"."

        added, list_title = [], None
        for item in items:
            params = {"user_id": user_id, "task_description": item}
            if parent:
                params["parent_id"] = parent["id"]
            elif target:
                params["list_id"] = target["id"]
            result = await self.mcp_server.call_tool("add_task", params)
            if not result["success"]:
                return f"Sorry, I couldn't add \"{item}\": {result['message']}"
            added.append(item)
            list_title = result["task"]["list_title"]

        if parent:
            where = f"under item {parent['number']} \"{parent['description']}\""
            if len(added) == 1:
                return f"Added \"{added[0]}\" {where}. ✅"
            return f"Added {len(added)} sub-items {where}: " + ", ".join(added) + ". ✅"
        if len(added) == 1:
            return f"Added \"{added[0]}\" to {list_title}. ✅"
        return f"Added {len(added)} items to {list_title}: " + ", ".join(added) + ". ✅"

    def _handle_list_tasks(
        self, intent: Dict[str, Any], lists: List[Dict[str, Any]], tasks: List[Dict[str, Any]]
    ) -> str:
        """
        Show lists with their items. Item numbers are the same everywhere,
        so "task 3" means the same thing whether or not a filter is applied.
        """
        if not lists:
            return "You don't have any lists yet. Try \"Create a list called Groceries\"."

        status_filter = intent.get("status_filter")

        # "show Groceries", "show me the groceries list", "what's in work"
        name = re.sub(r"^(me\s+)?(all\s+)?(of\s+)?(my\s+|the\s+)?", "", intent.get("rest", ""), flags=re.IGNORECASE)
        name = re.sub(r"\s*\b(lists?|tasks?|items?|todos?)\s*[?.!]*$", "", name, flags=re.IGNORECASE)
        name = re.sub(r"^(completed|done|finished|incomplete|pending|active|remaining)\s*", "", name, flags=re.IGNORECASE)
        selected = self._find_list(name, lists) if name.strip() else None
        shown_lists = [selected] if selected else lists

        def matches(task: Dict[str, Any]) -> bool:
            return not status_filter or task["status"] == status_filter

        def line(task: Dict[str, Any], indent: str) -> str:
            status_icon = "✓" if task["status"] == "completed" else "○"
            due_text = f" (due: {task['due_date']})" if task.get("due_date") else ""
            separator = " " if task.get("parent") else ". "
            return f"{indent}{task['number']}{separator}{status_icon} {task['description']}{due_text}"

        lines = []
        for todo_list in shown_lists:
            items = todo_list["tasks"]
            everything = items + [sub for t in items for sub in t.get("subtasks", [])]
            done = sum(1 for t in everything if t["status"] == "completed")
            lines.append(f"🗂️ {todo_list['title']} ({done}/{len(everything)} done)")

            shown_any = False
            for task in items:
                subtasks = [s for s in task.get("subtasks", []) if matches(s)]
                if not matches(task) and not subtasks:
                    continue
                shown_any = True
                lines.append(line(task, "   "))
                for subtask in subtasks:
                    lines.append(line(subtask, "        "))
            if not shown_any:
                lines.append("   (no items)" if not items else f"   (no {status_filter} items)")
            lines.append("")

        header = f"Here's your {selected['title']} list:" if selected else "Here are your lists:"
        return header + "\n" + "\n".join(lines).rstrip()

    async def _handle_complete_task(
        self, intent: Dict[str, Any], user_id: str, lists: List[Dict[str, Any]], tasks: List[Dict[str, Any]]
    ) -> str:
        """
        Handle completing (or reopening) an item
        """
        if not tasks:
            return "You don't have any items yet."

        task, error = self._resolve_task(intent.get("task_ref", ""), lists, tasks)
        if error:
            return error

        if intent.get("reopen"):
            if task["status"] != "completed":
                return f"{self._describe(task)} is already active."
            result = await self.mcp_server.call_tool(
                "update_task", {"user_id": user_id, "task_id": task["id"], "new_status": "incomplete"}
            )
            if result["success"]:
                return f"Reopened {self._describe(task)} in {task['list_title']}."
            return f"Sorry, I couldn't reopen that item: {result['message']}"

        if task["status"] == "completed":
            return f"{self._describe(task)} is already completed. ✓"

        result = await self.mcp_server.call_tool("complete_task", {"user_id": user_id, "task_id": task["id"]})

        if result["success"]:
            return f"Marked {self._describe(task)} in {task['list_title']} as done. ✓"
        else:
            return f"Sorry, I couldn't complete that item: {result['message']}"

    async def _handle_update_task(
        self, intent: Dict[str, Any], user_id: str, lists: List[Dict[str, Any]], tasks: List[Dict[str, Any]]
    ) -> str:
        """
        Handle editing an item's text ("edit task 1 to X", "rename milk in Groceries to oat milk"),
        or renaming a list when the name given is a list title ("rename Groceries to Shopping").
        """
        rest = intent.get("rest", "")
        splits = [
            (rest[:m.start()], rest[m.end():])
            for m in re.finditer(r"\s+(?:to|into|->)\s+|\s*:\s*", rest, re.IGNORECASE)
        ]
        if not splits:
            return "What should I change it to? Try \"Edit task 1 to buy oat milk\"."

        # Prefer a split whose left side names an item exactly ("rename go to gym to go to the gym")
        for ref, new_text in splits:
            task, _ = self._resolve_task(ref, lists, tasks, exact_only=True)
            if task:
                return await self._update_task_text(task, new_text, user_id)

        # Then a list title ("rename Groceries to Shopping")
        for ref, new_text in splits:
            todo_list = self._find_list(ref, lists)
            if todo_list:
                return await self._rename_list(todo_list, new_text, user_id)

        # Finally the first split that matches a single item
        ref, new_text = splits[0]
        task, error = self._resolve_task(ref, lists, tasks)
        if error:
            return error
        return await self._update_task_text(task, new_text, user_id)

    async def _update_task_text(self, task: Dict[str, Any], new_text: str, user_id: str) -> str:
        new_text = new_text.strip(" .!\"'")
        if not new_text:
            return f"What should item {task['number']} say instead? Try \"Edit task {task['number']} to <new text>\"."
        if _norm(new_text) == _norm(task["description"]):
            return f"Item {task['number']} already says \"{task['description']}\"."

        result = await self.mcp_server.call_tool(
            "update_task", {"user_id": user_id, "task_id": task["id"], "new_description": new_text}
        )

        if result["success"]:
            where = f"under \"{task['parent']['description']}\"" if task.get("parent") else f"in {task['list_title']}"
            return f"Updated item {task['number']} {where}: \"{task['description']}\" → \"{new_text}\". ✏️"
        else:
            return f"Sorry, I couldn't update that item: {result['message']}"

    async def _handle_delete_task(
        self, intent: Dict[str, Any], user_id: str, lists: List[Dict[str, Any]], tasks: List[Dict[str, Any]]
    ) -> str:
        """
        Handle deleting an item, or all completed items
        """
        ref = self._clean_ref(intent.get("task_ref", ""))

        if re.fullmatch(r"(all\s+)?(the\s+)?(my\s+)?(completed|done|finished)(\s+(tasks?|todos?|items?))?", ref, re.IGNORECASE):
            completed = [t for t in tasks if t["status"] == "completed"]
            if not completed:
                return "You don't have any completed items to clear."
            completed_ids = {t["id"] for t in completed}
            for task in completed:
                if task.get("parent") and task["parent"]["id"] in completed_ids:
                    continue  # removed together with its parent
                await self.mcp_server.call_tool("delete_task", {"user_id": user_id, "task_id": task["id"]})
            return f"Cleared {len(completed)} completed item(s). 🧹"

        if re.fullmatch(r"(all|everything|all\s+(my\s+)?(tasks?|todos?|items?|lists?))", ref, re.IGNORECASE):
            return "To keep your data safe, I delete one item or one list at a time, or all completed items with \"Clear completed tasks\"."

        if not tasks:
            return "You don't have any items to delete."

        task, error = self._resolve_task(intent.get("task_ref", ""), lists, tasks)
        if error:
            # A bare list title is not deleted without the word "list", to avoid accidents
            todo_list = self._find_list(ref, lists)
            if todo_list:
                return (
                    f"\"{todo_list['title']}\" is a list with {todo_list['task_count']} item(s). "
                    f"To delete the whole list, say \"Delete the {todo_list['title']} list\"."
                )
            return error

        result = await self.mcp_server.call_tool("delete_task", {"user_id": user_id, "task_id": task["id"]})

        if result["success"]:
            if task.get("parent"):
                return f"Deleted {self._describe(task)}. 🗑️"
            extra = result.get("deleted_subtasks", 0)
            and_subs = f" and its {extra} sub-item(s)" if extra else ""
            return f"Deleted \"{task['description']}\"{and_subs} from {task['list_title']}. 🗑️"
        else:
            return f"Sorry, I couldn't delete that item: {result['message']}"


# Create a global agent instance
todo_agent = TodoAgent()


def get_todo_agent():
    """
    Get the global todo agent instance
    """
    return todo_agent
