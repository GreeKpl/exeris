import React from "react";
import {Panel, FormGroup, FormControl, Button, Col} from "react-bootstrap";

class SpeakPanel extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      text: "",
    };

    this.onChange = this.onChange.bind(this);
  }

  onChange(event) {
    const textValue = event.target.value;
    this.setState({text: textValue});
  }

  render() {
    let label;
    switch (this.props.speakType) {
      case "speakTo":
        label = "Speak to";
        break;
      case "whisperTo":
        label = "Whisper to";
        break;
      case "aloud":
      default:
        label = "Say aloud";
    }

    return <Panel>
      <form>
        <FormGroup
          controlId="speakMessage"
        >
          <Col sm={10}>
            <FormControl
              type="text"
              value={this.state.text}
              placeholder="Enter message..."
              onChange={this.onChange}
            />
          </Col>
          <Col componentClass={Button} sm={2}>
            {label}
          </Col>
        </FormGroup>
      </form>
    </Panel>;
  }
}


export default SpeakPanel;
