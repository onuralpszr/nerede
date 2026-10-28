"""Step 5: zero-shot classification. Route a question to a category with no training data.

Symmetric task: the same "task: classification" prefix goes on labels and inputs.
"""

from nerede import get_embedder
from nerede.router import Router

router = Router(get_embedder())
for text in [
    "akşam rakı içmek için güzel bir yer",
    "how do I pay for the metro?",
    "çocuklarla gidilecek müze",
    "best spot to watch the sunset",
    "yağmurlu bir günde ne yapsam",
    "I want to buy old books",
    "DevFest bileti ne kadar?",
    "how many dimensions does the embedding have",
]:
    label, score = router.route(text)
    print(f"{label:>12}  {score:.3f}  {text}")
