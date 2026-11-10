# Jarvis Voice Command & Navigation Specifications

## CMD-001: Wake-Prefix Detection & Phonetic Desktop Parsing

When evaluating transcribed speech, the commander shall detect wake prefixes and extract target desktop space numbers.

Acceptance Criteria:
- AC-CMD-001.1: When text begins with a supported wake prefix, the commander shall recognize the input as a voice command.
- AC-CMD-001.2: When stripping wake prefixes, the commander shall return the cleaned command body without punctuation.
- AC-CMD-001.3: When given a desktop navigation phrase, the commander shall parse target space numbers from digits or spoken words.
- AC-CMD-001.4: If a command does not match any recognized desktop navigation pattern, then the commander shall return no action.

## CMD-002: Quartz Desktop Space Switching & Command Routing

When handling voice commands, the commander shall route execution to Quartz key combinations and announce action outcomes.

Acceptance Criteria:
- AC-CMD-002.1: When given a valid space number between 1 and 9, the commander shall post Quartz Control and number key events.
- AC-CMD-002.2: If a space number is outside the range 1 to 9, then the commander shall announce that the number is out of bounds.
- AC-CMD-002.3: If a command is recognized but unparseable, then the commander shall announce that the command is not recognized.
- AC-CMD-002.4: If text is standard dictation without a wake prefix, then the commander shall return false to allow text injection.

