import * as Immutable from "immutable";
import {characterReducerDecorator} from "../util/characterReducerDecorator";

export const SELECT_SPEAKING_TARGET = "exeris-front/speechReducer/SELECT_SPEAKING_TARGET";
export const UPDATE_TEXT = "exeris-front/speechReducer/UPDATE_TEXT";

export const SPEECH_TYPE_ALOUD = "SPEECH_TYPE_ALOUD";
export const SPEECH_TYPE_SPEAK_TO = "SPEECH_TYPE_SPEAK_TO";
export const SPEECH_TYPE_WHISPER_TO = "SPEECH_TYPE_WHISPER_TO";

export const updateText = (characterId, newText) => {
  return {
    type: UPDATE_TEXT,
    newText: newText,
    characterId: characterId,
  };
};

export const selectSpeakingTarget = (characterId, targetId, speechType) => {
  if ([SPEECH_TYPE_ALOUD, SPEECH_TYPE_SPEAK_TO, SPEECH_TYPE_WHISPER_TO].indexOf(speechType) === -1) {
    return {};
  }

  return {
    type: SELECT_SPEAKING_TARGET,
    targetId: targetId,
    speechType: speechType,
    characterId: characterId,
  };
};


export const speechReducer = (state =
                                Immutable.fromJS({
                                  "text": "",
                                  "speechType": SPEECH_TYPE_ALOUD,
                                  "speechTargetId": null,
                                }), action) => {
  switch (action.type) {
    case SELECT_SPEAKING_TARGET:
      return state.withMutations(st =>
        st.set("speechType", action.speechType)
          .set("speechTargetId", action.targetId)
      );
    case UPDATE_TEXT:
      return state.set("text", action.newText);
    default:
      return state;
  }
};

export const decoratedSpeechReducer = characterReducerDecorator(speechReducer);

export const getText = state => state.get("text");

export const getSpeechTargetId = state => state.get("speechTargetId");

export const getSpeechType = state => state.get("speechType");

export const fromSpeechState = (state, characterId) =>
  state.getIn(["speech", characterId], Immutable.Map());
