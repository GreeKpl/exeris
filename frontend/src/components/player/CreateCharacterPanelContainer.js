import {connect} from "react-redux";
import {createNewCharacter} from "../../modules/player";
import React from "react";
import {Button, Col, Form} from "react-bootstrap";

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
    return <Form autoComplete="off">
      <Form.Group controlId="characterName">
        <Col sm={3}>
          Character name
        </Col>
        <Col sm={9}>
          <Form.Control type="text"
                        placeholder="Character name"
                        value={this.state.characterName}
                        onChange={this.onNameChange}/>
        </Col>
      </Form.Group>

      <Form.Group>
        <Col sm={{span: 9, offset: 3}}>
          <Button type="submit" onClick={this.onClick}>
            Create character
          </Button>
        </Col>
      </Form.Group>
    </Form>
  }
}

export {CreateCharacterPanel};

const mapStateToProps = (state) => {
  return {};
};

const mapDispatchToProps = (dispatch) => {
  return {
    onCreateCharacterClick: characterName => dispatch(createNewCharacter(characterName)),
  }
};

const CreateCharacterPanelContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CreateCharacterPanel);

export default CreateCharacterPanelContainer;
