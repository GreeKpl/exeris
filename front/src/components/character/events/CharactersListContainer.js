import {connect} from "react-redux";
import CharactersList from "./CharactersList";
import {
  fromCharactersAroundState,
  getCharactersAround,
  requestCharactersAround,
  getCombatId,
  getCombatName
} from "../../../modules/charactersAround";
import {
  getSpeechTargetId,
  getSpeechType,
  fromSpeechState,
  selectSpeakingTarget,
  SPEECH_TYPE_SPEAK_TO,
  SPEECH_TYPE_WHISPER_TO,
  SPEECH_TYPE_ALOUD,
} from "../../../modules/speech";
import {requestCharacterDetails} from "../../../modules/topPanel";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    charactersAround: getCharactersAround(fromCharactersAroundState(state, ownProps.characterId)),
    speechTarget: getSpeechTargetId(fromSpeechState(state, ownProps.characterId)),
    speechType: getSpeechType(fromSpeechState(state, ownProps.characterId)),
    combatName: getCombatName(fromCharactersAroundState(state, ownProps.characterId)),
    combatId: getCombatId(fromCharactersAroundState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    requestState: () => dispatch(requestCharactersAround(ownProps.characterId)),
    onSelectSpeak: targetId => () => dispatch(selectSpeakingTarget(ownProps.characterId, targetId, SPEECH_TYPE_SPEAK_TO)),
    onSelectWhisper: targetId => () => dispatch(selectSpeakingTarget(ownProps.characterId, targetId, SPEECH_TYPE_WHISPER_TO)),
    onSelectSayAloud: () => dispatch(selectSpeakingTarget(ownProps.characterId, null, SPEECH_TYPE_ALOUD)),
    onShowMore: targetId => () => dispatch(requestCharacterDetails(ownProps.characterId, targetId)),
  }
};

const CharactersListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharactersList);

export default CharactersListContainer;
