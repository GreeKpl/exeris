import {connect} from "react-redux";
import * as Immutable from "immutable";
import {
  fromCharactersAroundState,
  getIdsOfCharactersAround,
  requestCharactersAround,
} from "../../../modules/charactersAround";
import {fromEntitiesState, getEntityInfos} from "../../../modules/entities";
import {
  fromSpeechState,
  getSpeechTargetId,
  getSpeechType,
  selectSpeakingTarget,
  SPEECH_TYPE_ALOUD,
  SPEECH_TYPE_SPEAK_TO,
  SPEECH_TYPE_WHISPER_TO,
} from "../../../modules/speech";
import {parseHtmlToComponents} from "../../../util/parseDynamicName";
import React from "react";
import {Button, Card, ListGroup, ListGroupItem} from "react-bootstrap";
import speakBubble from "../../../images/speakBubble.png";
import whisperBubble from "../../../images/whisperBubble.png";


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

const CharacterEntry = ({id, nameComponent, isSpeechTarget, speechType, onSelectSpeak, onSelectWhisper}) => (
  <ListGroupItem>
    <SpeakBubble targetId={id}
                                 isSpeechTarget={isSpeechTarget}
                                 speechType={speechType}
                                 onClick={onSelectSpeak}/>
    <WhisperBubble targetId={id}
                   isSpeechTarget={isSpeechTarget}
                   speechType={speechType}
                   onClick={onSelectWhisper}/>
     {nameComponent}
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
    return (
      <Card>
        <Card.Header>
          <div>
            People around
            <Button
            variant={this.props.speechType === SPEECH_TYPE_ALOUD ? "primary" : "default"}
            onClick={this.props.onSelectSayAloud}>Say to all</Button>
          </div>
        </Card.Header>
        <Card.Body>
          <ListGroup fill="true">
            {this.props.charactersAround.map(this.createCharacterEntry)}
          </ListGroup>
        </Card.Body>
      </Card>
    );
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
  }
};

const CharactersListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharactersList);

export default CharactersListContainer;
