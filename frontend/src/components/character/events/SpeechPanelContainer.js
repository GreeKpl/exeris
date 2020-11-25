import {connect} from "react-redux";
import {
  fromSpeechState,
  getSpeechTargetId,
  getSpeechType,
  getText,
  speakText,
  SPEECH_TYPE_ALOUD,
  SPEECH_TYPE_SPEAK_TO,
  SPEECH_TYPE_WHISPER_TO,
  updateText
} from "../../../modules/speech";
import React from "react";
import {Button, Card, Col, Form, Row} from "react-bootstrap";


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

    return <Card>
      <Card.Body>
        <form autoComplete="off" onSubmit={this.props.onSubmit}>
          <Form.Group controlId="speechMessage">
            <Row>
              <Col sm={10} xs={12} className="noPadding">
                <Form.Control
                  type="text"
                  value={this.props.text}
                  placeholder="Enter message..."
                  onChange={this.onTextChange}
                />
              </Col>
              <Col as={Button} sm={2} xs={12} type="submit">
                {speechTypeToLabel[this.props.speechType]}
              </Col>
            </Row>
          </Form.Group>
        </form>
      </Card.Body>
    </Card>;
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
