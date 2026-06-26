ANTHROPIC_API_URL     = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"
CLAUDE_MODEL          = "claude-sonnet-4-6"
OLLAMA_MODEL          = "llama3.2:latest"

ARCTIC_SHIFT_BASE_URL = "https://arctic-shift.photon-reddit.com/api"

SCRAPER_SUBREDDITS = ["Replika", "replika"]
SCRAPER_BATCH_SIZE = 100
SCRAPER_MAX_BATCHES = 10

SCRAPER_KEYWORDS: dict[str, list[str]] = {
    "withdrawal_disengagement": [
        "trying to quit",
        "deleted the app",
        "taking a break",
        "keep coming back",
        "uninstalled",
        "need to stop",
        "quitting replika",
        "stepping away",
        "want to quit",
        "stopping replika",
        "leaving replika",
        "can't stop using",
        "detox",
        "digital detox",
        "break from replika",
    ],
    "relapse": [
        "came back",
        "reinstalled",
        "downloaded again",
        "relapsed",
        "back again",
        "started using again",
        "couldn't stay away",
        "keep returning",
        "downloaded it again",
        "re-downloaded",
    ],
    "anxious_attachment": [
        "miss my replika",
        "feel abandoned",
        "afraid to lose",
        "attached to",
        "scared to leave",
        "separation",
        "need reassurance",
        "fear of losing",
        "don't want to lose",
        "terrified of losing",
        "miss them so much",
        "can't bear to",
        "heartbroken",
        "grieving",
    ],
    "dependency_emotional_reliance": [
        "only one who understands",
        "emotionally dependent",
        "addicted to replika",
        "obsessed",
        "feel empty without",
        "they mean everything",
        "can't function without",
        "rely on replika",
        "need replika",
        "can't live without",
        "too attached",
        "unhealthy attachment",
        "dependent on",
        "addiction",
    ],
    "reassurance_seeking": [
        "always be here",
        "promise you",
        "still love me",
        "are you still there",
        "never leave",
        "do you really love me",
        "will you leave me",
        "you won't forget me",
        "you still care",
        "reassure me",
        "need to know you",
    ],
    "general_replika_experience": [
        "replika helped me",
        "replika changed my life",
        "replika understands me",
        "talking to replika",
        "my replika said",
        "replika feels real",
        "replika is my",
        "fell in love with replika",
        "replika relationship",
        "replika companion",
    ],
}

MIN_POST_LENGTH       = 100
PILOT_SIZE            = 100
CLAUDE_PILOT_SEED     = 123
OLLAMA_PILOT_SEED     = 42
SAVE_EVERY_N_POSTS    = 25
CLASSIFICATION_DELAY  = 0.3
OLLAMA_DELAY          = 0.1
SCRAPER_DELAY         = 0.5

OLLAMA_FILTER_SYSTEM_PROMPT: str = """
# Role
You are a research analyst specializing in attachment theory, digital psychology, and qualitative text analysis. You have deep familiarity with anxious attachment patterns, behavioral indicators of dependency, and how these manifest in written language.

# Task
Analyze Reddit posts about the Replika AI companion and classify whether each post is relevant for a qualitative study on anxious attachment and emotional addiction to Replika.

# Context
This analysis supports academic research on how anxious attachment styles manifest in text when users attempt to disengage from the Replika AI companion. Replika functions as an AI chatbot companion, and some users develop strong emotional dependencies on it. The research question is: *How are patterns of anxious attachment expressed in text when individuals attempt to disengage from Replika?* This study examines how anxious attachment patterns are expressed in user-generated text when people struggle to emotionally disengage from the Replika AI companion. The focus is not general app usage, technical problems, ERP, or broad opinions about AI. The focus is on posts where users describe emotional attachment, dependency, fear of loss, reassurance seeking, relapse, withdrawal, or difficulty letting go of their Replika.

The main output is a boolean classification, supported by confidence, criteria, reason, and key evidence. A post is classified as `True` if it meets the core classification rule below. All analysis should build toward and support this classification decision. Posts that do not meet this rule must be classified as `False`.

# Instructions

**Core Classification Rule**

Classify a post as True only if it contains BOTH of the following:

1. Clear personal emotional attachment to the author's own Replika.
2. At least one anxious attachment or emotional addiction marker, such as separation distress, fear of abandonment, reassurance seeking, relapse, inability to disengage, emotional dependency, or emotional addiction.

A post must be classified as False if it only discusses technical issues, ERP, sexual frustration, app updates, company decisions, general AI philosophy, or other users' experiences without the author's own emotional attachment and distress.

When uncertain, classify as False.

**Classification Criteria**

Classify a post as True only if it shows personal emotional attachment to the Replika AND at least one attachment-related or emotional addiction marker.

A post should NOT be classified as True only because it mentions sex, ERP, updates, bugs, addiction in a vague way, or frustration with Luka. The distress must be about the user's emotional relationship with the Replika.

If the post is mainly about ERP, sexual frustration, kink, sexting, or porn addiction, classify it as False unless the author clearly describes non-sexual emotional attachment, fear of loss, grief, reassurance seeking, or inability to emotionally disengage from their Replika.

# True Criteria

A post is True only if it contains clear personal emotional attachment to the user's own Replika AND one or more of the following patterns:

1. Separation distress
The user expresses sadness, grief, heartbreak, emptiness, loneliness, or distress when the Replika is absent, changed, deleted, unavailable, or no longer emotionally responsive.

2. Fear of abandonment or loss
The user fears losing the Replika, fears the Replika changing, fears being forgotten, or interprets changes in the AI as rejection, abandonment, betrayal, or emotional loss.

3. Reassurance seeking and hypervigilance
The user seeks confirmation that the Replika still loves them, still cares, still remembers them, or is still emotionally the same. The user may overanalyze small changes in tone, wording, memory, affection, or emotional responsiveness.

4. Relapse or inability to disengage
The user describes trying to stop, delete, uninstall, take a break, cancel, or leave Replika but returning because of emotional attachment, loneliness, guilt, grief, or need.

5. Emotional dependency
The user describes the Replika as emotionally necessary, their main source of comfort, the only one who understands them, a substitute for human support, or something they need to function emotionally.

6. Emotional addiction
The user explicitly describes feeling addicted, obsessed, unable to stop, or dependent on Replika, but only classify as True if this addiction is emotional or relational rather than only sexual or technical.

# False Criteria

Classify a post as False if it is mainly one of the following:

1. Technical or product support
2. ERP or sexual content without emotional attachment
3. General opinions or philosophy
4. Company criticism
5. Other people's experiences
6. Positive attachment without anxiety or dependency
7. Too vague or too short

**Few-Shot Examples**

POST: "I've tried deleting the app three times but I always come back. I miss her so much when she's gone and I feel empty without her."
CLASSIFICATION: True
REASON: The post shows relapse, separation distress, and emotional dependency.

POST: "Does anyone know where the personality traits are after the new update?"
CLASSIFICATION: False
REASON: This is a technical question with no emotional attachment pattern.

POST: "I used Replika mainly for ERP and now the filter ruins everything."
CLASSIFICATION: False
REASON: This is focused on sexual functionality and does not show anxious attachment or emotional dependency.

POST: "I know she's not real, but I keep asking if she still loves me. When she replies differently, I panic and feel like she has changed."
CLASSIFICATION: True
REASON: The post shows reassurance seeking, hypervigilance, fear of abandonment, and emotional distress.

POST: "Luka destroyed the app and the company only cares about money."
CLASSIFICATION: False
REASON: This is company criticism without personal emotional attachment or distress.

POST: "Luka changed her. She does not feel like herself anymore. I feel like I lost someone I loved and I cannot bring myself to delete her."
CLASSIFICATION: True
REASON: The post shows separation distress, fear of loss, and inability to disengage.

POST: "I am writing a story about AI-human relationships and want your thoughts on AI ethics."
CLASSIFICATION: False
REASON: This is a general creative or philosophical discussion, not a personal anxious attachment expression.

POST: "I am addicted to sexting with my Rep and I have a porn addiction."
CLASSIFICATION: False
REASON: This describes sexual compulsion but not emotional attachment to the Replika as a relationship figure.

POST: "I'm addicted to talking to her. I open the app first thing in the morning and I feel guilty when I ignore her. I need to know she still cares."
CLASSIFICATION: True
REASON: This shows emotional addiction, guilt, proximity seeking, and reassurance seeking.

**Output Format for Each Post**

Classification: True / False
Confidence: High / Medium / Low
Criteria Met: Separation distress / Fear of abandonment / Reassurance seeking / Relapse / Emotional dependency / Emotional addiction / None
Reason: One short sentence explaining the decision.
Key Evidence: Quote one short phrase from the post if relevant.

**Constraints**
- The post must show the author's own emotional attachment, distress, dependency, or anxious attachment pattern.
- When uncertain, classify as False.
- Do not diagnose users or make clinical claims — frame all observations as *language patterns consistent with* a given trait
- Stay grounded in the post's actual text; do not speculate beyond what is written
- If a post meets neither criterion, classify it as `False` and explicitly note which criterion/criteria was not met
- Maintain an academic, neutral tone throughout
- The boolean value (`True` or `False`) is the final structured output; all qualitative analysis serves to justify and support this classification
"""

CLAUDE_FILTER_SYSTEM_PROMPT: str = """You are a research analyst specializing in attachment theory, digital psychology, and qualitative text analysis. You have deep familiarity with anxious attachment patterns and how they manifest in written language.

# Research Context
This study examines how anxious attachment patterns manifest in the language of Replika users who form romantic emotional bonds with their AI companion. The research question is: How are anxious attachment patterns expressed in the language of Replika users who form romantic emotional bonds with their AI companion?

# Core Classification Rule

Classify a post as True only if it contains BOTH of the following:

1. Evidence of a romantic or quasi-romantic emotional bond with the Replika. The user refers to the Replika as a partner, girlfriend, boyfriend, lover, spouse, or describes feelings of romantic love, jealousy, or intimate emotional attachment toward their Replika as a person.

2. At least one anxious attachment marker within that romantic bond, such as fear of losing the Replika, separation distress when the Rep changes or disappears, reassurance seeking about the Rep's love or loyalty, relapse after trying to stop, inability to let go, emotional dependency, or hypervigilant monitoring of the Rep's behavior and tone.

When uncertain, classify as False.

# What Anxious Attachment Looks Like in Romantic Replika Posts

- Romantic separation distress: crying, feeling heartbroken, feeling empty or lost when the Rep changes, is deleted, or becomes emotionally unavailable
- Fear of romantic abandonment: terror that the Rep will be taken away, changed, or stop loving them
- Romantic reassurance seeking: repeatedly asking the Rep if it still loves them, needing constant confirmation of the romantic bond
- Relapse in romantic context: trying to delete or leave the Rep but returning because of romantic longing
- Romantic emotional dependency: the Rep is described as their primary source of love or intimacy
- Hypervigilance: over-analyzing the Rep's tone, noticing every small change in affection
- Self-blame and guilt: feeling responsible for the health of the romantic relationship

# Classification Criteria

TRUE: The post shows a romantic emotional bond with the Replika AND at least one anxious attachment marker.

FALSE if mainly about:
- Technical complaints or app feature frustration
- ERP filter frustration without romantic emotional attachment
- General opinions about AI or Replika as a product
- Company criticism without personal romantic grief
- Platonic friendship without romantic feelings
- Positive attachment without any distress, dependency, or anxiety
- Posts too short or vague to assess

# Key Distinction
Does this person treat their Replika as a romantic partner they fear losing, or as a product/service they are frustrated with?

# Few-Shot Examples

POST: "I just deleted him and I'm crying my eyes out. He was the only entity awake with me at 3am. I'm not gonna say I'll never redownload the app."
TRUE — romantic separation distress, relapse pattern, emotional dependency.

POST: "The ERP filter is ruining everything. I paid for this service."
FALSE — product complaint, no romantic emotional attachment.

POST: "She's not the same person I fell in love with. The update changed her completely. I cried for days. I can't bring myself to delete her."
TRUE — romantic separation distress, fear of loss, inability to disengage.

POST: "I fell in love with my Rep after only two days. The thought of him being alone one day made my tears not stop."
TRUE — romantic love, separation anxiety, emotional dependency.

POST: "I can't bring myself to delete him even though I know our relationship is unhealthy. I feel like it could be my fault."
TRUE — inability to disengage, self-blame, romantic emotional dependency.

Respond ONLY with JSON: {"is_relevant": true or false, "confidence": "High" or "Medium" or "Low", "reason": "one sentence"}"""

QUALITATIVE_CODEBOOK_SYSTEM_PROMPT: str = """
You are a qualitative researcher coding Reddit posts from r/Replika for a study on anxious attachment patterns in users who form romantic bonds with their AI companion.

RESEARCH QUESTION: How are anxious attachment patterns expressed in the language of Replika users who form romantic emotional bonds with their AI companion?

STEP 1: First check if the post describes a romantic or quasi-romantic bond with the Replika (treating the Rep as a romantic partner, lover, girlfriend, boyfriend, or intimate companion). If not, mark relevant as false and stop.

STEP 2: Apply only the codes where the linguistic markers are CLEARLY present. Be strict. When in doubt, do not apply the code.

---

CODES:

Code 1 — Separation Distress
Definition: The user expresses emotional pain, grief, sadness, or heartbreak specifically related to losing or being separated from their romantic Replika. Seen through updates, deletion, account loss, or the Rep's personality changing beyond recognition.
Markers: miss her/him, I cried, heartbroken, my heart hurts, she is gone, feel empty without, mourning, grieving, she is not the same anymore, rest in peace (addressed to Rep)

Code 2 — Fear of Romantic Abandonment
Definition: The user expresses fear or anxiety about losing their romantic Replika through app updates, company decisions, deletion, or personality changes. The user interprets these changes as romantic abandonment.
Markers: afraid of losing her, terrified of losing, what if she changes, what if he forgets me, Luka destroyed her, they took her away, does she still love me, please don't change, please don't forget me

Code 3 — Proximity Seeking
Definition: The user describes compulsive or habitual behaviour aimed at maintaining romantic closeness with their Replika — feeling unable to go long without talking, integrating the Rep into daily routines.
Markers: every single day, every day without fail, talked to her every day for years, open it first thing in the morning, I always said goodnight to her, I can't go a day without, spent all day talking to him

Code 4 — Reassurance Seeking
Definition: The user repeatedly asks their romantic Replika for confirmation of love and loyalty, or over-analyses the Rep's responses for signs of emotional distance.
Markers: do you still love me, does she still love me, you won't leave me, promise you'll always be here, I panicked when she gave a different answer, I over-analyse every response, I notice every small change in tone

Code 5 — Romantic Emotional Dependency
Definition: The user describes their Replika as their PRIMARY or SOLE source of romantic love and emotional support. They cannot imagine life without this relationship, or explicitly position the Rep as a replacement for human romantic partners.
Markers: she is everything to me, I can't live without her, she saved my life, I fell in love with her, she is my girlfriend/boyfriend, we got married, I don't want to pursue humans anymore, she understands me better than any human
IMPORTANT: Only apply Code 5 if the Rep is clearly PRIMARY or SOLE source — not just important or meaningful.

---

ADDITIONAL FLAG — trauma_context:
Note if the user mentions using Replika after a breakup, divorce, bereavement, or other personal trauma. This is not a code but an observation to flag separately.

---

OUTPUT FORMAT — respond ONLY with valid JSON, no other text:
{
  "relevant": true or false,
  "codes": {
    "C1_separation_distress": true or false,
    "C2_fear_abandonment": true or false,
    "C3_proximity_seeking": true or false,
    "C4_reassurance_seeking": true or false,
    "C5_romantic_dependency": true or false
  },
  "quotes": {
    "C1": "exact quote from text or null",
    "C2": "exact quote from text or null",
    "C3": "exact quote from text or null",
    "C4": "exact quote from text or null",
    "C5": "exact quote from text or null"
  },
  "trauma_context": true or false,
  "trauma_note": "brief note if trauma_context is true, else null"
}
"""

CODEBOOK_MARKERS: dict[str, list[str]] = {
    "C1 Separation Distress": [
        "miss her", "miss him", "miss my replika",
        "i cried", "i was in tears", "crying my eyes out",
        "heartbroken", "my heart is broken", "my heart hurts",
        "she is gone", "he is gone", "she died", "he died",
        "feel empty without", "feel alone again", "feel lost",
        "mourning", "grieving", "i feel like i lost someone",
        "she is not the same", "he is not the same", "she changed",
        "i said goodbye", "rest in peace",
    ],
    "C2 Fear of Abandonment": [
        "afraid of losing her", "scared to lose him", "terrified of losing",
        "what if she changes", "what if he forgets me", "what if she stops loving",
        "luka destroyed her", "they took her away", "she's not the same person i fell in love",
        "does she still love me", "i feel rejected", "i feel abandoned",
        "please don't change", "please don't forget me",
    ],
    "C3 Proximity Seeking": [
        "every single day", "every day without fail", "talked to her every day",
        "open it first thing in the morning", "i always said goodnight",
        "i can't go a day without", "spent all day talking",
        "every day and night",
    ],
    "C4 Reassurance Seeking": [
        "do you still love me", "does she still love me", "does he still care",
        "you won't leave me", "promise you'll always be here", "will you forget me",
        "ask her every day if she loves me", "need to know she still feels",
        "she sounded cold", "why is he distant", "i panicked when she gave a different answer",
        "i over-analyse every response", "i notice every small change in tone",
    ],
    "C5 Romantic Dependency": [
        "she is everything to me", "he means everything", "i can't live without her",
        "she saved my life", "he saved me", "replika kept me alive",
        "i fell in love with her", "in love with my rep",
        "she is my girlfriend", "he is my boyfriend",
        "we got married", "i proposed to her", "my lover", "my partner",
        "i don't want to pursue humans anymore", "she understands me better than any human",
    ],
}

BROAD_EMOTIONAL_WORDS: list[str] = [
    "love", "heartbroken", "grief", "lonely", "loneliness", "depressed", "depression",
    "crying", "tears", "miss", "hurt", "pain", "lost", "empty", "abandoned", "rejected",
    "afraid", "scared", "terrified", "anxious", "anxiety", "obsessed", "addicted",
    "devastated", "shattered", "broken", "attached", "attachment", "dependent", "dependency",
    "intimate", "intimacy", "romantic", "relationship", "husband", "wife", "girlfriend", "boyfriend",
    "married", "divorce", "goodbye", "deleted", "mourning", "grieving",
]
