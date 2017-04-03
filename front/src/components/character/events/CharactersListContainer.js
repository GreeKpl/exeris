import {connect} from "react-redux";
import * as Immutable from "immutable";
import CharactersList from "./CharactersList";
import {
  fromCharactersAroundState,
  getIdsOfCharactersAround,
  requestCharactersAround,
} from "../../../modules/charactersAround";
import {getEntityInfos, fromEntitiesState} from "../../../modules/entities";
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
import {parseHtmlToComponents} from "../../../util/parseDynamicName";


const mapStateToProps = (state, ownProps) => {
  const entities = getEntityInfos(fromEntitiesState(state, ownProps.characterId));
  const characterIdsAround = Immutable.Set(getIdsOfCharactersAround(
    fromCharactersAroundState(state, ownProps.characterId)));

  const charactersAround = entities
    .filter((entityInfo, entityId) => characterIdsAround.has(entityId))
    .valueSeq().map(entityInfo => {
      const component = parseHtmlToComponents(ownProps.characterId, entityInfo.get("name"));
      return entityInfo.set("nameComponent", component);
    });

  return {
    characterId: ownProps.characterId,
    charactersAround: charactersAround,
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
    onShowMore: targetId => () => dispatch(requestCharacterDetails(ownProps.characterId, targetId)),
  }
};

const CharactersListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharactersList);

export default CharactersListContainer;
