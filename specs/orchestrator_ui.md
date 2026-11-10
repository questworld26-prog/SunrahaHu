# Application Orchestration & User Interface Specifications

## APP-001: Dictation State Machine, Debounce Locking & Worker Pipeline

While managing dictation sessions, the application orchestrator shall coordinate audio recording, voice cues, transcription, and command handling with debounce locking.

Acceptance Criteria:
- AC-APP-001.1: When toggle is invoked in idle state, the orchestrator shall transition to recording and start audio capture.
- AC-APP-001.2: When toggle is invoked while recording, the orchestrator shall stop capture, transition to transcribing, and spawn transcription.
- AC-APP-001.3: If toggle is invoked while a transition is already in progress, then the orchestrator shall debounce duplicate requests.
- AC-APP-001.4: When silence or timeout callbacks fire from the recorder, the orchestrator shall automatically stop and transcribe.
- AC-APP-001.5: If microphone startup fails, then the orchestrator shall reset recording state to idle and log the failure.

## UI-001: macOS Menu Bar Controller & Dynamic Microphone Selector

While running in the background, the menu bar controller shall display current dictation status, language options, and microphone input devices.

Acceptance Criteria:
- AC-UI-001.1: When initialized, the menu bar controller shall construct status, language, and microphone menu items.
- AC-UI-001.2: When a microphone is selected from the menu, the menu bar controller shall update the active input device in the recorder.
- AC-UI-001.3: When status changes occur from background worker threads, the controller shall dispatch status title updates safely.

## HKY-001: Global Keyboard Hotkey Listener

Where global hotkeys are enabled, the hotkey listener shall register and start keyboard listener threads and release listener resources upon stopping.

Acceptance Criteria:
- AC-HKY-001.1: When started, the hotkey listener shall instantiate and launch the global hotkey monitor thread.
- AC-HKY-001.2: When stopped, the hotkey listener shall stop the underlying keyboard listener and clear listener references.

