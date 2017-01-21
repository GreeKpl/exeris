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
  SPEECH_TYPE_WHISPER_TO
} from "../../src/modules/speech";
import * as Immutable from "immutable";

describe('(speech) speechReducer', () => {

  it('Should initialize with initial state.', () => {
    expect(speechReducer(undefined, {})).to.equal(Immutable.fromJS({
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
    expect(state).to.equal(previousState);
  });

  it('Should update the text when a new text is supplied.', () => {
    const previousState = Immutable.fromJS({
      "text": "abc",
      "speechTargetId": null,
      "speechType": SPEECH_TYPE_ALOUD,
    });
    let state = speechReducer(previousState, updateText(0, "defs"));
    expect(state).to.equal(previousState.set("text", "defs"));
  });

  it('Should update the speech target and type when a new one is supplied.', () => {
    const previousState = Immutable.fromJS({
      "text": "abc",
      "speechTargetId": null,
      "speechType": SPEECH_TYPE_ALOUD,
    });
    let state = speechReducer(previousState, selectSpeakingTarget(0, "HEH_ID", SPEECH_TYPE_WHISPER_TO));
    expect(state).to.equal(Immutable.fromJS({
      "text": "abc",
      "speechTargetId": "HEH_ID",
      "speechType": SPEECH_TYPE_WHISPER_TO,
    }));
  });

  it("Should return empty action when invalid speech type is specified", () => {
    expect(selectSpeakingTarget(1, "AHA", "INVALID_SPEECH")).to.deep.equal({});
  });

  it('Should update the speech of a specified character.', () => {
    let state = decoratedSpeechReducer(undefined, {});
    state = decoratedSpeechReducer(state, updateText("DEF", "new text"));
    state = decoratedSpeechReducer(state, selectSpeakingTarget("OWN_CHAR", "TARGET", SPEECH_TYPE_WHISPER_TO));
    const globalState = Immutable.Map({speech: state});
    expect(getText(fromSpeechState(globalState, "DEF"))).to.equal("new text");
    expect(getSpeechTargetId(fromSpeechState(globalState, "OWN_CHAR"))).to.equal("TARGET");
    expect(getSpeechType(fromSpeechState(globalState, "OWN_CHAR"))).to.equal(SPEECH_TYPE_WHISPER_TO);
  });
});
