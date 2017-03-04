import React from "react";
import {
  Panel,
  Grid,
  Row,
  ListGroupItem,
  Col,
  Glyphicon,
  ControlLabel,
  Form,
  FormGroup,
  FormControl,
  Button
} from "react-bootstrap";
import {fireOnEnter} from "../../eventUtil";
import "./style.scss";


const CharacterNameEditBox = ({newName, onNewNameChange, onSubmitName}) => {

  return <FormGroup
    controlId="newCharacterName">
    <Col componentClass={ControlLabel} sm={4} key="characterNameLabel">
      Name
    </Col>
    <Col sm={8}>
      <Grid fluid>
        <Row>
          <Col>
            <FormControl type="text" onKeyPress={fireOnEnter(onSubmitName)} onChange={onNewNameChange}
                         value={newName}/>
          </Col>
        </Row>
        <Row>
          <Col>
            <Button style={{width: "50%"}} onClick={onSubmitName}>OK</Button>
          </Col>
        </Row>
      </Grid>
    </Col>
  </FormGroup>;
};

class CharacterPanel extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      nameBeingEdited: false,
    };

    this.handleSubmitName = this.handleSubmitName.bind(this);
    this.startEditingName = this.startEditingName.bind(this);
    this.onNewNameChange = this.onNewNameChange.bind(this);
  }

  handleSubmitName() {
    this.props.onSubmitName(this.state.newName);
    this.setState({
      nameBeingEdited: false,
    });
  }

  startEditingName() {
    this.setState({
      nameBeingEdited: true,
      newName: this.props.rawName,
    });
  }

  onNewNameChange(event) {
    const newName = event.target.value;
    this.setState({
      nameBeingEdited: true,
      newName: newName,
    });
  }

  render() {
    return <Panel header="Character info">
      <Grid fluid>
        <Row>
          <Col xs={12} md={3}>
            <Form autoComplete="off" horizontal>
              {this.state.nameBeingEdited ? <CharacterNameEditBox
                  newName={this.state.newName}
                  onNewNameChange={this.onNewNameChange}
                  onSubmitName={this.handleSubmitName}/> : <FormGroup controlId="characterName">
                  <Col componentClass={ControlLabel} sm={4} key="characterNameLabel">
                    Name
                  </Col>
                  <Col sm={8}
                       onClick={this.startEditingName}
                       componentClass={FormControl.Static}
                  className="CharacterPanel-ClickableName">
                    {this.props.rawName} <Glyphicon glyph="pencil"/>
                  </Col>
                </FormGroup>}
              <FormGroup controlId="characterLocation">
                <Col componentClass={ControlLabel} sm={4}>
                  Location
                </Col>
                <Col componentClass={FormControl.Static} sm={8}>
                  {this.props.locationName} <Glyphicon glyph="globe"/>
                </Col>
              </FormGroup>
              {this.props.workIntent &&
              <FormGroup controlId="characterWork">
                <Col componentClass={ControlLabel} sm={4}>
                  Working on
                </Col>
                <Col componentClass={FormControl.Static} sm={8}>
                  {this.props.workIntent}
                </Col>
              </FormGroup>}
              {this.props.combatIntent &&
              <FormGroup controlId="characterCombat">
                <Col componentClass={ControlLabel} sm={4}>
                  Fighting in
                </Col>
                <Col componentClass={FormControl.Static} sm={8}>
                  {this.props.combatIntent}
                </Col>
              </FormGroup>}
            </Form>
          </Col>
          <Col xs={12} md={3}>
            <FormGroup controlId="inventory">
              <ControlLabel>Equipment</ControlLabel>
              <FormControl componentClass="list-group">
                {this.props.equipment.map(itemName => <ListGroupItem>{itemName}</ListGroupItem>)}
              </FormControl>
            </FormGroup>
          </Col>
          <Col xs={12} md={6}>
            <Form autoComplete="off" horizontal>
              <FormGroup controlId="shortDescription">
                <Col componentClass={ControlLabel} sm={3}>
                  Short description
                </Col>
                <Col componentClass={FormControl.Static} sm={9}>
                  {this.props.shortDescription}
                </Col>
              </FormGroup>
              <FormGroup controlId="longDescription">
                <Col componentClass={ControlLabel} sm={3}>
                  Long description
                </Col>
                <Col componentClass={FormControl.Static} sm={9}>
                  {this.props.longDescription}
                </Col>
              </FormGroup>
            </Form>
          </Col>
        </Row>
      </Grid>
    </Panel>;
  }
}


export default CharacterPanel;
