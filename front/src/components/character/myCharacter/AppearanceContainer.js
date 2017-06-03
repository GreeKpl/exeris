import {connect} from "react-redux";
import {getMyCharacterInfoFromMyCharacterState} from "../../../modules/myCharacter";
import React from "react";
import {FormGroup, ControlLabel, FormControl, Form, Col, Panel} from "react-bootstrap";

export const Appearance = ({shortDescription, longDescription}) => {
  return (
    <Panel header="Appearance">
      <Form autoComplete="off" horizontal>
        <FormGroup controlId="shortDescriptionTextarea">
          <Col componentClass={ControlLabel} sm={3}>
            Short description
          </Col>
          <Col sm={9}>
            <FormControl componentClass="textarea"
                         value={shortDescription}
                         readOnly
                         placeholder="Enter short description shown directly on characters list..." rows={1}/>
          </Col>
        </FormGroup>
        <FormGroup controlId="longDescriptionTextarea">
          <Col componentClass={ControlLabel} sm={3}>
            Long description
          </Col>
          <Col sm={9}>
            <FormControl componentClass="textarea"
                         value={longDescription}
                         readOnly
                         placeholder="Enter long description..."/>
          </Col>
        </FormGroup>
      </Form>
    </Panel>);
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
