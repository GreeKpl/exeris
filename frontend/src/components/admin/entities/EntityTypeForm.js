import {
  CLASSES, getSelectedEntityType, fromGameContentState, getAllPropertyNames,
  requestUpdateOfEntityType
} from "../../../modules/gameContent";
import React from "react";
import {Button, Col, Form, Row} from "react-bootstrap";
import {connect} from "react-redux";
import {reduxForm, getFormValues, Field, FieldArray} from "redux-form/immutable";
import HorizontalFormInput from "../../commons/HorizontalFormInput";
import FormCheckbox from "../../commons/FormCheckbox";
import EntityTypePropertiesForm from "./EntityTypePropertiesForm";


const EntityTypeRawForm = ({typeParams, ...otherParams}) => {
  switch (typeParams.get("class")) {
    case CLASSES.ENTITY_ITEM:
      return <ItemTypeForm typeParams={typeParams} {...otherParams}/>;
    default:
      return <div>Unsupported entity class</div>;
  }
};


const EntityTypeForm = reduxForm({
  form: 'entityTypeManagement',
})(EntityTypeRawForm);


const mapEntityStateToProps = (state) => {
  const selectedEntityType = getSelectedEntityType(fromGameContentState(state));
  return {
    typeParams: selectedEntityType,
    selectedEntityTypeName: selectedEntityType ? selectedEntityType.get("name") : null,
    initialValues: selectedEntityType,
    propertyNames: getAllPropertyNames(fromGameContentState(state)),
  };
};

const mapEntityDispatchToProps = (dispatch) => {
  return {
    onSubmit: data => {
      dispatch(requestUpdateOfEntityType(data.toJS()));
    },
  };
};

const EntityTypeFormContainer = connect(
  mapEntityStateToProps,
  mapEntityDispatchToProps
)(EntityTypeForm);


export default EntityTypeFormContainer;


const ItemTypeForm = ({typeParams, handleSubmit, onSubmit, pristine, reset, submitting, propertyNames}) => {
  return <Form autoComplete="off"  onSubmit={handleSubmit(onSubmit)}>
    <Field name="name"
           component={HorizontalFormInput}
           componentClass="input"
           type="text"
           label="Name"
           placeholder="Unique name..."
           key="nameField"/>
    <Field name="stackable"
           component={FormCheckbox}
           label="Stackable"
           key="stackableField"/>
    <Field name="portable"
           component={FormCheckbox}
           label="Portable"
           key="portableField"/>
    <FieldArray name="properties" props={
      {
        propertyNames
      }
    } component={EntityTypePropertiesForm}/>
    <Row>
      <Col sm={{span: 9, offset: 3}}>
        <Button type="submit" disabled={submitting || pristine}>Confirm</Button>
      </Col>
    </Row>
  </Form>;
};
