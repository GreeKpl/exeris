import {connect} from "react-redux";
import {createActivityFromRecipe, fromRecipesState, getSelectedRecipe} from "../../../modules/recipes";
import {Field, getFormValues, reduxForm} from "redux-form/immutable";

import React from "react";
import {Button, Col, Form, ListGroup, ListGroupItem} from "react-bootstrap";
import HorizontalFormInput from "../../commons/HorizontalFormInput";
import HorizontalFormInfo from "../../commons/HorizontalFormInfo";


const RequirementInfo = ({info, infoKey, label}) =>
  info.get(infoKey).size > 0 ?
    <Field name={infoKey}
           component={HorizontalFormInfo}
           label={label}
           key={infoKey}
           lines={info.get(infoKey)}
    /> : null;

export class ActionDetailsRaw extends React.Component {

  constructor(props) {
    super(props);

    this.renderAdditionalFormInputs = this.renderAdditionalFormInputs.bind(this);
    this.getAmount = this.getAmount.bind(this);
  }

  componentDidUpdate(prevProps) {
    if (prevProps.recipeDetails.get("id") !== this.props.recipeDetails.get("id")
      || prevProps.characterId !== this.props.characterId) {
      this.props.reset();
    }
  }

  renderAdditionalFormInputs() {
    let renderedFormInputs = [];
    for (let formInput of this.props.recipeDetails.get("requiredFormInputs")) {
      if (formInput.get("type") === "AmountInput") {
        renderedFormInputs.push(
          <Field name={formInput.get("name")}
                 component={HorizontalFormInput}
                 componentClass="input"
                 type="text"
                 label={formInput.get("name")}
                 placeholder="Set amount"
                 key={formInput.get("name")}
          />);
      } else if (formInput.get("type") === "NameInput") {
        renderedFormInputs.push(
          <Field name={formInput.get("name")}
                 component={HorizontalFormInput}
                 componentClass="input"
                 type="text"
                 label={formInput.get("name")}
                 placeholder="Enter name..."
                 key={"form-" + formInput.get("name")}
          />);
      } else if (formInput.get("type") === "WorkDaysInput") {
        renderedFormInputs.push(
          <Field name={formInput.get("name")}
                 component={HorizontalFormInput}
                 componentClass="input"
                 type="text"
                 label="Work days"
                 placeholder="Set number"
                 key={formInput.get("name")}
          />);
      } else if (formInput.get("type") === "AnimalResourceLevel") {
        renderedFormInputs.push(
          <Form.Group key={"form-" + formInput.get("name")} controlId={"form-" + formInput.get("name")}>
            <Col componentClass={Form.Label} sm={3}>
              Animal resource level
            </Col>
            <Col sm={9} componentClass={Form.Control.Static}>
              {formInput.get("args").get("resource_type")}
            </Col>
          </Form.Group>);
      }
    }
    return renderedFormInputs;
  }

  getAmount() {
    if (!this.formState) {
      return 1;
    } else {
      this.formState.get("amount", 1);
    }
  }

  render() {
    const recipeDetails = this.props.recipeDetails;

    if (recipeDetails.size === 0) {
      return null;
    }

    const {handleSubmit, pristine, reset, submitting} = this.props;

    return (
      <Form autoComplete="off" horizontal onSubmit={handleSubmit}>
        {recipeDetails.get("errorMessages").size > 0 &&
        <Form.Group key="errorMessages" controlId="errorMessages">
          <Col componentClass={Form.Label} sm={3}>
            Errors
          </Col>
          <Col sm={9}>
            <ListGroup>
              {recipeDetails.get("errorMessages").map(message => <ListGroupItem
                key={message}>{message}</ListGroupItem>)}
            </ListGroup>
          </Col>
        </Form.Group>}
        <RequirementInfo info={recipeDetails}
                         infoKey="name"
                         label="Name"/>
        {recipeDetails.get("requiresSubject") &&
        <Field name="activitySubject"
               component={HorizontalFormInput}
               as="select"
               label="Subject of activity"
               placeholder="Select subject..."
               key="activitySubject">
          {recipeDetails.get("subjects").map(subject =>
            <option value={subject.get("id")} key={subject.get("id")}>
              {subject.get("name")}
            </option>)}
        </Field>}
        <RequirementInfo info={recipeDetails}
                         infoKey="requiredInput"
                         label="Required input"/>
        <RequirementInfo info={recipeDetails}
                         infoKey="requiredTools"
                         label="Required tools"/>
        <RequirementInfo info={recipeDetails}
                         infoKey="requiredMachines"
                         label="Required machines"/>
        <Form.Group key="requiredDays" controlId="requiredDays">
          <Col componentClass={Form.Label} sm={3}>
            Required days
          </Col>
          <Col sm={9} componentClass={Form.Control.Static}>
            {recipeDetails.get("requiredDays") * this.getAmount()} = {recipeDetails.get("requiredDays")}
            {" "}
            x {this.getAmount()}
          </Col>
        </Form.Group>
        <RequirementInfo info={recipeDetails}
                         infoKey="requiredSkills"
                         label="Required skills"/>
        {this.renderAdditionalFormInputs()}
        <Form.Group key="submit">
          <Col smOffset={3} sm={9}>
            <Button type="submit" disabled={recipeDetails.get("errorMessages").size > 0}>
              Start an activity
            </Button>
          </Col>
        </Form.Group>
      </Form>);
  }
}


export const ActionDetails = reduxForm({
  form: 'recipeDetails',
})(ActionDetailsRaw);


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    recipeDetails: getSelectedRecipe(fromRecipesState(state, ownProps.characterId)),
    formState: getFormValues('recipeDetails')(state),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onSubmit: data => {
      dispatch(createActivityFromRecipe(ownProps.characterId, data.toJS()));
    },
  }
};

const ActionDetailsContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ActionDetails);

export default ActionDetailsContainer;
