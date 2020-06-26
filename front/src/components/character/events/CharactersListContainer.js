import {connect} from "react-redux";
import * as Immutable from "immutable";
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
import {requestCharacterDetails} from "../../../modules/details";
import {parseHtmlToComponents} from "../../../util/parseDynamicName";
import React from "react";
import {Panel, ListGroup, ListGroupItem, Button} from "react-bootstrap";
import speakBubble from "../../../images/speakBubble.png";
import whisperBubble from "../../../images/whisperBubble.png";
import actionDots from "../../../images/threeDots.png";


const SpeakBubble = ({targetId, onClick, isSpeechTarget, speechType}) =>
  <img className={[
    "Character-CharactersList-actionIcon",
    (isSpeechTarget && speechType === SPEECH_TYPE_SPEAK_TO) ? "Character-CharactersList-actionIcon--active" : "",
  ].join(" ")}
       onClick={onClick}
       src={speakBubble}/>;
const WhisperBubble = ({targetId, onClick, isSpeechTarget, speechType}) =>
  <img className={[
    "Character-CharactersList-actionIcon",
    (isSpeechTarget && speechType === SPEECH_TYPE_WHISPER_TO) ? "Character-CharactersList-actionIcon--active" : "",
  ].join(" ")}
       onClick={onClick}
       src={whisperBubble}/>;

const CharacterEntry = ({id, nameComponent, isSpeechTarget, speechType, onSelectSpeak, onSelectWhisper, onShowMore}) => (
  <ListGroupItem>
    {nameComponent} <SpeakBubble targetId={id}
                                 isSpeechTarget={isSpeechTarget}
                                 speechType={speechType}
                                 onClick={onSelectSpeak}/>
    <WhisperBubble targetId={id}
                   isSpeechTarget={isSpeechTarget}
                   speechType={speechType}
                   onClick={onSelectWhisper}/>
    <img src={actionDots} className="Character-CharactersList-actionIcon" onClick={onShowMore}/>
  </ListGroupItem>
);


export class CharactersList extends React.Component {

  constructor(props) {
    super(props);

    this.createCharacterEntry = this.createCharacterEntry.bind(this);
  }

  componentDidMount() {
    this.props.requestState();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.characterId !== this.props.characterId) {
      this.props.requestState();
    }
  }

  render() {
    return <Panel header={<div>People around <Button
      bsStyle={this.props.speechType === SPEECH_TYPE_ALOUD ? "primary" : "default"}
      onClick={this.props.onSelectSayAloud}>Say to all</Button></div>}>
      <ListGroup fill="true">
        {this.props.charactersAround.map(this.createCharacterEntry)}
      </ListGroup>
    </Panel>;
  }

  createCharacterEntry(character) {
    return <CharacterEntry
      key={character.get("id")}
      id={character.get("id")}
      nameComponent={character.get("nameComponent")}
      combatName={character.get("combatName")}
      combatId={character.get("combatId")}
      onSelectSpeak={this.props.onSelectSpeak(character.get("id"))}
      onSelectWhisper={this.props.onSelectWhisper(character.get("id"))}
      onShowMore={this.props.onShowMore(character.get("id"))}
      isSpeechTarget={this.props.speechTarget === character.get("id")}
      speechType={this.props.speechType}
    />;
  }
}


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
