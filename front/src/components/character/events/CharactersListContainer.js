import {connect} from "react-redux";
import CharactersList from "./CharactersList";
import {
  fromCharactersAroundState,
  getCharactersAround,
  requestCharactersAround
} from "../../../modules/charactersAround";
import {
  getSpeechTargetId,
  getSpeechType,
  fromSpeechState,
  selectSpeakingTarget,
  SPEECH_TYPE_SPEAK_TO,
  SPEECH_TYPE_WHISPER_TO,
  SPEECH_TYPE_ALOUD
} from "../../../modules/speech";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    charactersAround: getCharactersAround(fromCharactersAroundState(state, ownProps.characterId)),
    speechTarget: getSpeechTargetId(fromSpeechState(state, ownProps.characterId)),
    speechType: getSpeechType(fromSpeechState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    requestState: () => dispatch(requestCharactersAround(ownProps.characterId)),
    onSelectSpeak: targetId => () => dispatch(selectSpeakingTarget(ownProps.characterId, targetId, SPEECH_TYPE_SPEAK_TO)),
    onSelectWhisper: targetId => () => dispatch(selectSpeakingTarget(ownProps.characterId, targetId, SPEECH_TYPE_WHISPER_TO)),
    onSelectSayAloud: () => dispatch(selectSpeakingTarget(ownProps.characterId, null, SPEECH_TYPE_ALOUD)),
  }
};

const CharactersListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharactersList);

export default CharactersListContainer;
