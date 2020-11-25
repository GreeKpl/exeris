import {connect} from "react-redux";
import {fromDetailsState, getDetailsTarget, submitEditedName} from "../../../modules/details";
import {parseHtmlToComponents} from "../../../util/parseDynamicName";
import {fromEntitiesState, getEntityInfo} from "../../../modules/entities";
import React from "react";
import {fireOnEnter} from "../../eventUtil";
import "./style.scss";
import {Button, Card, Col, Container, Form, ListGroupItem, Row} from "react-bootstrap";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faCheck, faGlobe, faPencilAlt, faTimes} from "@fortawesome/free-solid-svg-icons";


const CharacterNameEditBox = ({newName, onNewNameChange, onSubmitName, onCancelName}) => {

  return <Form.Group
    controlId="newCharacterName">
    <Col componentClass={Form} sm={4} key="characterNameLabel">
      Name
    </Col>
    <Col sm={8}>
      <Container fluid>
        <Row>
          <Col>
            <Form.Control type="text" onKeyPress={fireOnEnter(onSubmitName)} onChange={onNewNameChange}
                          value={newName}/>
          </Col>
        </Row>
        <Row>
          <Col>
            <Button style={{width: "50%"}} onClick={onCancelName}><FontAwesomeIcon icon={faTimes}/></Button>
            <Button style={{width: "50%"}} onClick={onSubmitName}><FontAwesomeIcon icon={faCheck}/></Button>
          </Col>
        </Row>
      </Container>
    </Col>
  </Form.Group>;
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
    this.cancelEditingName = this.cancelEditingName.bind(this);
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

  cancelEditingName() {
    this.setState({
      nameBeingEdited: false,
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
    return (
      <Card>
        <Card.Header>Character info</Card.Header>
        <Card.Body>
          <Container fluid>
            <Row>
              <Col xs={12} md={3}>
                <Form autoComplete="off" horizontal>
                  {this.state.nameBeingEdited ? <CharacterNameEditBox
                    newName={this.state.newName}
                    onNewNameChange={this.onNewNameChange}
                    onSubmitName={this.handleSubmitName}
                    onCancelName={this.cancelEditingName}/> : <Form.Group controlId="characterName">
                    <Row>
                      <Col componentClass={Form} sm={4} key="characterNameLabel">
                        Name
                      </Col>
                      <Col sm={8}
                           onClick={this.startEditingName}
                           componentClass={Form.Control.Static}
                           className="CharacterPanel-ClickableName">
                        {this.props.rawName} <FontAwesomeIcon icon={faPencilAlt}/>
                      </Col>
                    </Row>
                  </Form.Group>}
                  <Form.Group controlId="characterLocation">
                    <Row>
                      <Col componentClass={Form} sm={4}>
                        Location
                      </Col>
                      <Col componentClass={Form.Control.Static} sm={8}>
                        {this.props.locationName} <FontAwesomeIcon icon={faGlobe}/>
                      </Col>
                    </Row>
                  </Form.Group>
                  {this.props.workIntent &&
                  <Form.Group controlId="characterWork">
                    <Row>
                      <Col componentClass={Form} sm={4}>
                        Working on
                      </Col>
                      <Col componentClass={Form.Control.Static} sm={8}>
                        {this.props.workIntent}
                      </Col>
                    </Row>
                  </Form.Group>}
                  {this.props.combatIntent &&
                  <Form.Group controlId="characterCombat">
                    <Row>
                      <Col componentClass={Form} sm={4}>
                        Fighting in
                      </Col>
                      <Col componentClass={Form.Control.Static} sm={8}>
                        {this.props.combatIntent}
                      </Col>
                    </Row>
                  </Form.Group>}
                </Form>
              </Col>
              <Col xs={12} md={3}>
                <Form.Group controlId="inventory">
                  <Form>Equipment</Form>
                  <Form.Control as="list-group">
                    {this.props.equipment.map((itemName, eqPart) => <ListGroupItem>{itemName}</ListGroupItem>)}
                  </Form.Control>
                </Form.Group>
              </Col>
              <Col xs={12} md={6}>
                <Form autoComplete="off" horizontal>
                  <Form.Group controlId="shortDescription">
                    <Row>
                      <Col componentClass={Form} sm={3}>
                        Short description
                      </Col>
                      <Col componentClass={Form.Control.Static} sm={9}>
                        {this.props.shortDescription}
                      </Col>
                    </Row>
                  </Form.Group>
                  <Form.Group controlId="longDescription">
                    <Row>
                      <Col componentClass={Form} sm={3}>
                        Long description
                      </Col>
                      <Col componentClass={Form.Control.Static} sm={9}>
                        {this.props.longDescription}
                      </Col>
                    </Row>
                  </Form.Group>
                </Form>
              </Col>
            </Row>
          </Container>
        </Card.Body>
      </Card>
    );
  }
}


export {CharacterPanel};


const mapStateToProps = (state, ownProps) => {
  const targetId = getDetailsTarget(fromDetailsState(state, ownProps.characterId));
  const entityInfo = getEntityInfo(targetId, fromEntitiesState(state, ownProps.characterId));

  const nameComponent = parseHtmlToComponents(ownProps.characterId, entityInfo.get("name"));
  return {
    characterId: ownProps.characterId,
    nameComponent: nameComponent,
    ...entityInfo.toObject(),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onSubmitName: newName => {
      dispatch(submitEditedName(ownProps.characterId, newName));
    },
  }
};

const CharacterPanelContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharacterPanel);

export default CharacterPanelContainer;
