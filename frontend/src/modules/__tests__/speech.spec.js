import {
  speechReducer,
  decoratedSpeechReducer,
  selectSpeakingTarget,
  updateText,
  getSpeechTargetId,
  getSpeechType,
  getText,
  fromSpeechState,
  SPEECH_TYPE_ALOUD,
  SPEECH_TYPE_WHISPER_TO,
  speakText,
  __RewireAPI__ as speechRewire, UPDATE_TEXT
} from "../speech";
import * as Immutable from "immutable";
import {createMockStore, DependenciesStubber} from "../../../tests/testUtils";

describe('(speech) speechReducer', () => {

  it('Should initialize with initial state.', () => {
    expect(speechReducer(undefined, {})).toEqual(Immutable.fromJS({
      "text": "",
      "speechTargetId": null,
      "speechType": SPEECH_TYPE_ALOUD,
    }));
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.fromJS({
      "text": "abc",
      "speechTargetId": null,
      "speechType": SPEECH_TYPE_ALOUD,
    });
    let state = speechReducer(previousState, {});
    expect(state).toEqual(previousState);
  });

  it('Should update the text when a new text is supplied.', () => {
    const previousState = Immutable.fromJS({
      "text": "abc",
      "speechTargetId": null,
      "speechType": SPEECH_TYPE_ALOUD,
    });
    let state = speechReducer(previousState, updateText(0, "defs"));
    expect(state).toEqual(previousState.set("text", "defs"));
  });

  it('Should update the speech target and type when a new one is supplied.', () => {
    const previousState = Immutable.fromJS({
      "text": "abc",
      "speechTargetId": null,
      "speechType": SPEECH_TYPE_ALOUD,
    });
    let state = speechReducer(previousState, selectSpeakingTarget(0, "HEH_ID", SPEECH_TYPE_WHISPER_TO));
    expect(state).toEqual(Immutable.fromJS({
      "text": "abc",
      "speechTargetId": "HEH_ID",
      "speechType": SPEECH_TYPE_WHISPER_TO,
    }));
  });

  it("Should return empty action when invalid speech type is specified", () => {
    expect(selectSpeakingTarget(1, "AHA", "INVALID_SPEECH")).toEqual({});
  });

  it('Should update the speech of a specified character.', () => {
    let state = decoratedSpeechReducer(undefined, {});
    state = decoratedSpeechReducer(state, updateText("DEF", "new text"));
    state = decoratedSpeechReducer(state, selectSpeakingTarget("OWN_CHAR", "TARGET", SPEECH_TYPE_WHISPER_TO));
    const globalState = Immutable.Map({speech: state});
    expect(getText(fromSpeechState(globalState, "DEF"))).toEqual("new text");
    expect(getSpeechTargetId(fromSpeechState(globalState, "OWN_CHAR"))).toEqual("TARGET");
    expect(getSpeechType(fromSpeechState(globalState, "OWN_CHAR"))).toEqual(SPEECH_TYPE_WHISPER_TO);
  });

  describe("Asynchronous socketio actions", () => {
    const charId = "DEF";

    it('Should request speaking in the backend.', () => {
      const store = createMockStore(Immutable.fromJS({
        speech: {
          [charId]: {
            text: "ABC",
            speechType: SPEECH_TYPE_ALOUD,
            speechTargetId: null,
          }
        },
      }), null);

      store.dispatch(speakText(charId));

      const actions = store.getActions();
      expect(actions).toHaveLength(1);
      expect(actions[0]).toEqual({
        type: UPDATE_TEXT,
        newText: "",
        characterId: charId,
      });
      store.socketCalledWith("character.say_aloud", charId, "ABC");
    });
  });
});
