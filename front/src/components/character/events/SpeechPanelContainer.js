import {connect} from "react-redux";
import {
  updateText,
  getText,
  getSpeechTargetId,
  getSpeechType,
  fromSpeechState,
  speakText
} from "../../../modules/speech";
import React from "react";
import {Panel, FormGroup, FormControl, Button, Col} from "react-bootstrap";
import {SPEECH_TYPE_WHISPER_TO, SPEECH_TYPE_ALOUD, SPEECH_TYPE_SPEAK_TO} from "../../../modules/speech";


export class SpeechPanel extends React.Component {
  constructor(props) {
    super(props);

    this.onTextChange = this.onTextChange.bind(this);
  }

  onTextChange(event) {
    const newText = event.target.value;
    this.props.onTextChange(newText);
  }

  render() {
    const speechTypeToLabel = {
      [SPEECH_TYPE_SPEAK_TO]: "Speak to",
      [SPEECH_TYPE_WHISPER_TO]: "Whisper to",
      [SPEECH_TYPE_ALOUD]: "Say aloud",
    };

    return <Panel>
      <form autoComplete="off" onSubmit={this.props.onSubmit}>
        <FormGroup
          controlId="speechMessage">
          <Col sm={10} xs={12} className="noPadding">
            <FormControl
              type="text"
              value={this.props.text}
              placeholder="Enter message..."
              onChange={this.onTextChange}
            />
          </Col>
          <Col componentClass={Button} sm={2} xs={12} type="submit">
            {speechTypeToLabel[this.props.speechType]}
          </Col>
        </FormGroup>
      </form>
    </Panel>;
  }
}

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    text: getText(fromSpeechState(state, ownProps.characterId)),
    speechTarget: getSpeechTargetId(fromSpeechState(state, ownProps.characterId)),
    speechType: getSpeechType(fromSpeechState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onTextChange: (newText) => dispatch(updateText(ownProps.characterId, newText)),
    onSubmit: event => {
      event.preventDefault();
      dispatch(speakText(ownProps.characterId));
    },
  }
};

const SpeechPanelContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(SpeechPanel);

export default SpeechPanelContainer;
