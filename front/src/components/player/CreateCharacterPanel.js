import React from "react";
import {FormControl, FormGroup, Form, Col, Button} from "react-bootstrap";

class CreateCharacterPanel extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      "characterName": "",
    };

    this.onClick = this.onClick.bind(this);
    this.onNameChange = this.onNameChange.bind(this);
  }

  onClick(event) {
    event.preventDefault();
    this.setState({"characterName": ""});
    this.props.onCreateCharacterClick(this.state.characterName);
  }

  onNameChange(event) {
    this.setState({
      "characterName": event.target.value,
    });
  }

  render() {
    return <Form horizontal>
      <FormGroup controlId="characterName">
        <Col sm={3}>
          Character name
        </Col>
        <Col sm={9}>
          <FormControl type="text"
                       placeholder="Character name"
                       value={this.state.characterName}
                       onChange={this.onNameChange}/>
        </Col>
      </FormGroup>

      <FormGroup>
        <Col smOffset={3} sm={9}>
          <Button type="submit" onClick={this.onClick}>
            Create character
          </Button>
        </Col>
      </FormGroup>
    </Form>
  }
}

export default CreateCharacterPanel;
