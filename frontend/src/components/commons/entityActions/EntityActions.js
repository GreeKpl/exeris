import React from "react";
import {
  Row,
  Col,
  Form,
  Button,
} from "react-bootstrap";
import {connect} from "react-redux";
import {reduxForm, getFormValues, Field} from "redux-form/immutable";
import HorizontalFormInput from "../HorizontalFormInput";
import {getSelectedEntities, getActionDetails, fromEntitiesState} from "../../../modules/entities";
import {performEntityAction} from "../../../modules/entities-actionsAddon";

const universalMapStateToProps = (state, ownProps) => {
  return {
    entityIds: getSelectedEntities(fromEntitiesState(state, ownProps.characterId)),
    details: getActionDetails(fromEntitiesState(state, ownProps.characterId)),
    formState: getFormValues('entityActionForm')(state),
  };
};

const TakeForm = ({entityIds, handleSubmit, onSubmit, pristine, reset, submitting}) => {
  return <Form horizontal autoComplete="off" onSubmit={handleSubmit(data =>
    onSubmit(data.set("entityIds", entityIds))
  )} style={{
    maxWidth: "400px",
  }}>
    <Field name="amount"
           component={HorizontalFormInput}
           componentClass="input"
           type="text"
           label="Amount"
           placeholder="Enter amount"
           key="amountField"/>
    <Row>
      <Col smOffset={3} sm={9}>
        <Button type="submit" disabled={submitting || pristine}>Confirm</Button>
      </Col>
    </Row>
  </Form>;
};

export const TakeFormContainer = connect(
  universalMapStateToProps,
  (dispatch, ownProps) => {
    return {
      onSubmit: data => {
        dispatch(performEntityAction(ownProps.characterId, "character.take_item",
          data.get("entityIds").toJS(), +data.get("amount")));
      },
    }
  }
)(reduxForm({
  form: 'entityActionForm',
})(TakeForm));


const DropForm = ({entityIds, handleSubmit, onSubmit, pristine, reset, submitting}) => {
  return <Form horizontal autoComplete="off" onSubmit={handleSubmit(data =>
    onSubmit(data.set("entityIds", entityIds))
  )} style={{
    maxWidth: "400px",
  }}>
    <Field name="amount"
           component={HorizontalFormInput}
           componentClass="input"
           type="text"
           label="Amount"
           placeholder="Enter amount"
           key="amountField"/>
    <Row>
      <Col smOffset={3} sm={9}>
        <Button type="submit" disabled={submitting || pristine}>Confirm</Button>
      </Col>
    </Row>
  </Form>;
};

export const DropFormContainer = connect(
  universalMapStateToProps,
  (dispatch, ownProps) => {
    return {
      onSubmit: data => {
        dispatch(performEntityAction(ownProps.characterId, "character.drop_item",
          data.get("entityIds").toJS(), +data.get("amount")));
      },
    }
  }
)(reduxForm({
  form: 'entityActionForm',
})(DropForm));


const GiveForm = ({entityIds, details, handleSubmit, onSubmit, pristine, reset, submitting}) => {
  return <Form horizontal autoComplete="off" onSubmit={handleSubmit(data =>
    onSubmit(data.set("entityIds", entityIds))
  )} style={{
    maxWidth: "400px",
  }}>
    <Field name="amount"
           component={HorizontalFormInput}
           componentClass="input"
           type="text"
           label="Amount"
           placeholder="Enter amount"
           key="amountField"/>
    <Field name="receiver"
           component={HorizontalFormInput}
           componentClass="select"
           label="Receiver"
           key="receiverField">
      <option value="1">John</option>
    </Field>
    <Row>
      <Col smOffset={3} sm={9}>
        <Button type="submit" disabled={submitting || pristine}>Confirm</Button>
      </Col>
    </Row>
  </Form>;
};

export const GiveFormContainer = connect(
  universalMapStateToProps,
  (dispatch, ownProps) => {
    return {
      onSubmit: data => {
        dispatch(performEntityAction(ownProps.characterId, "character.give_item",
          data.get("entityIds").toJS(), +data.get("amount")));
      },
    }
  }
)(reduxForm({
  form: 'entityActionForm',
})(GiveForm));


const EatForm = ({entityIds, handleSubmit, onSubmit, pristine, reset, submitting}) => {
  return <Form horizontal autoComplete="off" onSubmit={handleSubmit(data =>
    onSubmit(data.set("entityIds", entityIds))
  )} style={{
    maxWidth: "400px",
  }}>
    <Field name="amount"
           component={HorizontalFormInput}
           componentClass="input"
           type="text"
           label="Amount"
           placeholder="Enter amount"
           key="amountField"/>
    <Row>
      <Col smOffset={3} sm={9}>
        <Button type="submit" disabled={submitting || pristine}>Confirm</Button>
      </Col>
    </Row>
  </Form>;
};

export const EatFormContainer = connect(
  universalMapStateToProps,
  (dispatch, ownProps) => {
    return {
      onSubmit: data => {
        dispatch(performEntityAction(ownProps.characterId, "character.eat",
          data.get("entityIds").toJS(), +data.get("amount")));
      },
    }
  }
)(reduxForm({
  form: 'entityActionForm',
})(EatForm));


const PutIntoStorage = ({entityIds, details, handleSubmit, onSubmit, pristine, reset, submitting}) => {
  const singleStackableItem = entityIds.size === 1 && details.get("maxAmount") > 1;

  return <Form horizontal autoComplete="off" onSubmit={handleSubmit(data =>
    onSubmit(data.set("entityIds", entityIds))
  )} style={{
    maxWidth: "400px",
  }}>
    {singleStackableItem &&
    <Field name="amount"
           component={HorizontalFormInput}
           componentClass="input"
           type="text"
           label="Amount"
           placeholder="Enter amount"
           key="amountField"/>}
    <Field name="receiver"
           component={HorizontalFormInput}
           componentClass="select"
           label="Receiver"
           key="receiverField">
      {details.get("storages").map(storage =>
        <option value={storage.get("id")}>{storage.get("name")}</option>)}
    </Field>
    <Row>
      <Col smOffset={3} sm={9}>
        <Button type="submit" disabled={submitting || pristine}>Confirm</Button>
      </Col>
    </Row>
  </Form>;
};

export const PutIntoStorageFormContainer = connect(
  universalMapStateToProps,
  (dispatch, ownProps) => {
    return {
      onSubmit: data => {
        dispatch(performEntityAction(ownProps.characterId, "character.put_into_storage",
          data.get("entityIds").toJS(), +data.get("amount", null)));
      },
    }
  }
)(reduxForm({
  form: 'entityActionForm',
})(PutIntoStorage));
