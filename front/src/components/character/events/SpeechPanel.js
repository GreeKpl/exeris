import React from "react";
import {Panel, FormGroup, FormControl, Button, Col} from "react-bootstrap";
import {SPEECH_TYPE_WHISPER_TO, SPEECH_TYPE_ALOUD, SPEECH_TYPE_SPEAK_TO} from "../../../modules/speech";

class SpeechPanel extends React.Component {
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
      <form onSubmit={this.props.onSubmit}>
        <FormGroup
          controlId="speechMessage">
          <Col sm={10}>
            <FormControl
              type="text"
              value={this.props.text}
              placeholder="Enter message..."
              onChange={this.onTextChange}
            />
          </Col>
          <Col componentClass={Button} sm={2} type="submit">
            {speechTypeToLabel[this.props.speechType]}
          </Col>
        </FormGroup>
      </form>
    </Panel>;
  }
}


export default SpeechPanel;
