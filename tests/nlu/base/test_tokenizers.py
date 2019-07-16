# -*- coding: utf-8 -*-

from unittest.mock import patch
from rasa.nlu.training_data import TrainingData, Message
from tests.nlu import utilities
import copy


def test_whitespace():
    from rasa.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer

    tk = WhitespaceTokenizer()

    assert [t.text for t in tk.tokenize("Forecast for lunch")] == [
        "Forecast",
        "for",
        "lunch",
    ]

    assert [t.offset for t in tk.tokenize("Forecast for lunch")] == [0, 9, 13]

    # we ignore .,!?
    assert [t.text for t in tk.tokenize("hey ńöñàśçií how're you?")] == [
        "hey",
        "ńöñàśçií",
        "how",
        "re",
        "you",
    ]

    assert [t.offset for t in tk.tokenize("hey ńöñàśçií how're you?")] == [
        0,
        4,
        13,
        17,
        20,
    ]

    assert [t.text for t in tk.tokenize("привет! 10.000, ńöñàśçií. (how're you?)")] == [
        "привет",
        "10.000",
        "ńöñàśçií",
        "how",
        "re",
        "you",
    ]

    assert [
        t.offset for t in tk.tokenize("привет! 10.000, ńöñàśçií. (how're you?)")
    ] == [0, 8, 16, 27, 31, 34]

    # urls are single token
    assert [
        t.text
        for t in tk.tokenize(
            "https://www.google.com/search?client="
            "safari&rls=en&q="
            "i+like+rasa&ie=UTF-8&oe=UTF-8 "
            "https://rasa.com/docs/nlu/"
            "components/#tokenizer-whitespace"
        )
    ] == [
        "https://www.google.com/search?"
        "client=safari&rls=en&q=i+like+rasa&ie=UTF-8&oe=UTF-8",
        "https://rasa.com/docs/nlu/components/#tokenizer-whitespace",
    ]

    assert [
        t.offset
        for t in tk.tokenize(
            "https://www.google.com/search?client="
            "safari&rls=en&q="
            "i+like+rasa&ie=UTF-8&oe=UTF-8 "
            "https://rasa.com/docs/nlu/"
            "components/#tokenizer-whitespace"
        )
    ] == [0, 83]


def test_whitespace_with_case():
    print ("hello")
    from rasa.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer

    component_config = {"case_sensitive": False}
    tk = WhitespaceTokenizer(component_config)
    message = Message("Forecast for LUNCH")
    tk.process(message)
    assert message.text == "forecast for lunch"

    component_config = {"case_sensitive": True}
    tk = WhitespaceTokenizer(component_config)
    message = Message("Forecast for LUNCH")
    tk.process(message)
    assert message.text == "Forecast for LUNCH"

    component_config = {}
    tk = WhitespaceTokenizer(component_config)
    message = Message("Forecast for LUNCH")
    tk.process(message)
    assert message.text == "Forecast for LUNCH"

    _config = utilities.base_test_conf("supervised_embeddings")
    examples = [
        Message(
            "Any Mexican restaurant will do",
            {
                "intent": "restaurant_search",
                "entities": [
                    {"start": 4, "end": 11, "value": "Mexican", "entity": "cuisine"}
                ],
            },
        ),
        Message(
            "I want Tacos!",
            {
                "intent": "restaurant_search",
                "entities": [
                    {"start": 7, "end": 12, "value": "Mexican", "entity": "cuisine"}
                ],
            },
        ),
    ]

    examples_1 = copy.deepcopy(examples)
    examples_2 = copy.deepcopy(examples)

    component_config = {"case_sensitive": False}
    tk = WhitespaceTokenizer(component_config)
    tk.train(TrainingData(training_examples=examples), _config)
    assert examples[0].data.get("tokens")[0].text == "any"
    assert examples[0].data.get("tokens")[1].text == "mexican"
    assert examples[0].data.get("tokens")[2].text == "restaurant"
    assert examples[0].data.get("tokens")[3].text == "will"
    assert examples[0].data.get("tokens")[4].text == "do"
    assert examples[1].data.get("tokens")[0].text == "i"
    assert examples[1].data.get("tokens")[1].text == "want"
    assert examples[1].data.get("tokens")[2].text == "tacos"

    component_config = {"case_sensitive": True}
    tk = WhitespaceTokenizer(component_config)
    tk.train(TrainingData(training_examples=examples_1), _config)
    assert examples_1[0].data.get("tokens")[0].text == "Any"
    assert examples_1[0].data.get("tokens")[1].text == "Mexican"
    assert examples_1[0].data.get("tokens")[2].text == "restaurant"
    assert examples_1[0].data.get("tokens")[3].text == "will"
    assert examples_1[0].data.get("tokens")[4].text == "do"
    assert examples_1[1].data.get("tokens")[0].text == "I"
    assert examples_1[1].data.get("tokens")[1].text == "want"
    assert examples_1[1].data.get("tokens")[2].text == "Tacos"

    component_config = {}
    tk = WhitespaceTokenizer(component_config)
    tk.train(TrainingData(training_examples=examples_2), _config)
    assert examples_2[0].data.get("tokens")[0].text == "Any"
    assert examples_2[0].data.get("tokens")[1].text == "Mexican"
    assert examples_2[0].data.get("tokens")[2].text == "restaurant"
    assert examples_2[0].data.get("tokens")[3].text == "will"
    assert examples_2[0].data.get("tokens")[4].text == "do"
    assert examples_2[1].data.get("tokens")[0].text == "I"
    assert examples_2[1].data.get("tokens")[1].text == "want"
    assert examples_2[1].data.get("tokens")[2].text == "Tacos"


def test_spacy(spacy_nlp):
    from rasa.nlu.tokenizers.spacy_tokenizer import SpacyTokenizer

    tk = SpacyTokenizer()

    text = "Forecast for lunch"
    assert [t.text for t in tk.tokenize(spacy_nlp(text))] == [
        "Forecast",
        "for",
        "lunch",
    ]
    assert [t.offset for t in tk.tokenize(spacy_nlp(text))] == [0, 9, 13]

    text = "hey ńöñàśçií how're you?"
    assert [t.text for t in tk.tokenize(spacy_nlp(text))] == [
        "hey",
        "ńöñàśçií",
        "how",
        "'re",
        "you",
        "?",
    ]
    assert [t.offset for t in tk.tokenize(spacy_nlp(text))] == [0, 4, 13, 16, 20, 23]


def test_mitie():
    from rasa.nlu.tokenizers.mitie_tokenizer import MitieTokenizer

    tk = MitieTokenizer()

    text = "Forecast for lunch"
    assert [t.text for t in tk.tokenize(text)] == ["Forecast", "for", "lunch"]
    assert [t.offset for t in tk.tokenize(text)] == [0, 9, 13]

    text = "hey ńöñàśçií how're you?"
    assert [t.text for t in tk.tokenize(text)] == [
        "hey",
        "ńöñàśçií",
        "how",
        "'re",
        "you",
        "?",
    ]
    assert [t.offset for t in tk.tokenize(text)] == [0, 4, 13, 16, 20, 23]


def test_jieba():
    from rasa.nlu.tokenizers.jieba_tokenizer import JiebaTokenizer

    tk = JiebaTokenizer()

    assert [t.text for t in tk.tokenize("我想去吃兰州拉面")] == ["我", "想", "去", "吃", "兰州", "拉面"]

    assert [t.offset for t in tk.tokenize("我想去吃兰州拉面")] == [0, 1, 2, 3, 4, 6]

    assert [t.text for t in tk.tokenize("Micheal你好吗？")] == ["Micheal", "你好", "吗", "？"]

    assert [t.offset for t in tk.tokenize("Micheal你好吗？")] == [0, 7, 9, 10]


def test_jieba_load_dictionary(tmpdir_factory):
    from rasa.nlu.tokenizers.jieba_tokenizer import JiebaTokenizer

    dictionary_path = tmpdir_factory.mktemp("jieba_custom_dictionary").strpath

    component_config = {"dictionary_path": dictionary_path}

    with patch.object(
        JiebaTokenizer, "load_custom_dictionary", return_value=None
    ) as mock_method:
        tk = JiebaTokenizer(component_config)
        tk.tokenize("")

    mock_method.assert_called_once_with(dictionary_path)
