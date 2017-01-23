import React from "react";
import {Panel, ListGroup, ListGroupItem, Button, Glyphicon} from "react-bootstrap";
import speakBubble from "../../../images/speakBubble.png";
import whisperBubble from "../../../images/whisperBubble.png";
import actionDots from "../../../images/threeDots.png";
import {SPEECH_TYPE_ALOUD, SPEECH_TYPE_SPEAK_TO, SPEECH_TYPE_WHISPER_TO} from "../../../modules/speech";


const SpeakBubble = ({targetId, onClick, isSpeechTarget, speechType}) =>
  <img className={[
    "Character-CharactersList-actionIcon",
    (isSpeechTarget && speechType == SPEECH_TYPE_SPEAK_TO) ? "Character-CharactersList-actionIcon--active" : "",
  ].join(" ")}
       onClick={onClick}
       src={speakBubble}/>;
const WhisperBubble = ({targetId, onClick, isSpeechTarget, speechType}) =>
  <img className={[
    "Character-CharactersList-actionIcon",
    (isSpeechTarget && speechType == SPEECH_TYPE_WHISPER_TO) ? "Character-CharactersList-actionIcon--active" : "",
  ].join(" ")}
       onClick={onClick}
       src={whisperBubble}/>;

const CharacterEntry = ({id, name, isSpeechTarget, speechType, onSelectSpeak, onSelectWhisper, onShowMore}) => (
  <ListGroupItem>
    {name} <SpeakBubble targetId={id} isSpeechTarget={isSpeechTarget} speechType={speechType} onClick={onSelectSpeak}/>
    <WhisperBubble targetId={id} isSpeechTarget={isSpeechTarget} speechType={speechType} onClick={onSelectWhisper}/>
    <img src={actionDots} className="Character-CharactersList-actionIcon" onClick={onShowMore}/>
  </ListGroupItem>
);


class CharactersList extends React.Component {

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
      <ListGroup fill>
        {this.props.charactersAround.map(this.createCharacterEntry)}
      </ListGroup>
    </Panel>;
  }

  createCharacterEntry(character) {
    return <CharacterEntry
      key={character.get("id")}
      id={character.get("id")}
      name={character.get("name")}
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

export default CharactersList;
