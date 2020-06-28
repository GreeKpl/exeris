import {connect} from "react-redux";
import {getMyCharacterInfoFromMyCharacterState} from "../../../modules/myCharacter";
import React from "react";
import {Card, Col, Form} from "react-bootstrap";

export const Appearance = ({shortDescription, longDescription}) => {
  return (
    <Card>
      <Card.Header>Appearance</Card.Header>
      <Card.Body>
        <Form autoComplete="off" horizontal>
          <Form.Group controlId="shortDescriptionTextarea">
            <Col componentClass={Form.Label} sm={3}>
              Short description
            </Col>
            <Col sm={9}>
              <Form.Control componentClass="textarea"
                            value={shortDescription}
                            readOnly
                            placeholder="Enter short description shown directly on characters list..." rows={1}/>
            </Col>
          </Form.Group>
          <Form.Group controlId="longDescriptionTextarea">
            <Col componentClass={Form} sm={3}>
              Long description
            </Col>
            <Col sm={9}>
              <Form.Control componentClass="textarea"
                            value={longDescription}
                            readOnly
                            placeholder="Enter long description..."/>
            </Col>
          </Form.Group>
        </Form>
      </Card.Body>
    </Card>
  );
};


const mapStateToProps = (state, ownProps) => {
  const myCharacterInfo = getMyCharacterInfoFromMyCharacterState(state, ownProps.characterId);
  return {
    characterId: ownProps.characterId,
    shortDescription: myCharacterInfo.get("shortDescription", ""),
    longDescription: myCharacterInfo.get("longDescription", ""),
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const AppearanceContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Appearance);

export default AppearanceContainer;
