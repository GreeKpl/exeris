import React from "react";
import {FormGroup, Form, Col, FormControl, ControlLabel, Button, ListGroup, ListGroupItem} from "react-bootstrap";
import HorizontalFormInput from "../../commons/HorizontalFormInput";

import {Field, reduxForm} from 'redux-form/immutable';
import HorizontalFormInfo from "../../commons/HorizontalFormInfo";


const RequirementInfo = ({info, infoKey, label}) =>
  info.get(infoKey).size > 0 ?
    <Field name={infoKey}
           component={HorizontalFormInfo}
           label={label}
           key={infoKey}
           lines={info.get(infoKey)}
    /> : null;

class ActionDetails extends React.Component {

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
      if (formInput.get("type") == "AmountInput") {
        renderedFormInputs.push(
          <Field name={formInput.get("name")}
                 component={HorizontalFormInput}
                 componentClass="input"
                 type="text"
                 label={formInput.get("name")}
                 placeholder="Set amount"
                 key={formInput.get("name")}
          />);
      } else if (formInput.get("type") == "NameInput") {
        renderedFormInputs.push(
          <Field name={formInput.get("name")}
                 component={HorizontalFormInput}
                 componentClass="input"
                 type="text"
                 label={formInput.get("name")}
                 placeholder="Enter name..."
                 key={"form-" + formInput.get("name")}
          />);
      } else if (formInput.get("type") == "WorkDaysInput") {
        renderedFormInputs.push(
          <Field name={formInput.get("name")}
                 component={HorizontalFormInput}
                 componentClass="input"
                 type="text"
                 label="Work days"
                 placeholder="Set number"
                 key={formInput.get("name")}
          />);
      } else if (formInput.get("type") == "AnimalResourceLevel") {
        renderedFormInputs.push(
          <FormGroup key={"form-" + formInput.get("name")} controlId={"form-" + formInput.get("name")}>
            <Col componentClass={ControlLabel} sm={3}>
              Animal resource level
            </Col>
            <Col sm={9} componentClass={FormControl.Static}>
              {formInput.get("args").get("resource_type")}
            </Col>
          </FormGroup>);
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

    if (recipeDetails.size == 0) {
      return null;
    }

    const {handleSubmit, pristine, reset, submitting} = this.props;

    return (
      <Form horizontal onSubmit={handleSubmit}>
        {recipeDetails.get("errorMessages").size > 0 &&
        <FormGroup key="errorMessages" controlId="errorMessages">
          <Col componentClass={ControlLabel} sm={3}>
            Errors
          </Col>
          <Col sm={9}>
            <ListGroup>
              {recipeDetails.get("errorMessages").map(message => <ListGroupItem
                key={message}>{message}</ListGroupItem>)}
            </ListGroup>
          </Col>
        </FormGroup>}
        <RequirementInfo info={recipeDetails}
                         infoKey="name"
                         label="Name"/>
        {recipeDetails.get("requiresSubject") &&
        <Field name="activitySubject"
               component={HorizontalFormInput}
               componentClass="select"
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
        <FormGroup key="requiredDays" controlId="requiredDays">
          <Col componentClass={ControlLabel} sm={3}>
            Required days
          </Col>
          <Col sm={9} componentClass={FormControl.Static}>
            {recipeDetails.get("requiredDays") * this.getAmount()} = {recipeDetails.get("requiredDays")}
            {" "}
            x {this.getAmount()}
          </Col>
        </FormGroup>
        <RequirementInfo info={recipeDetails}
                         infoKey="requiredSkills"
                         label="Required skills"/>
        {this.renderAdditionalFormInputs()}
        <FormGroup key="submit">
          <Col smOffset={3} sm={9}>
            <Button type="submit" disabled={recipeDetails.get("errorMessages").size > 0}>
              Start an activity
            </Button>
          </Col>
        </FormGroup>
      </Form>);
  }
}

export default reduxForm({
  form: 'recipeDetails',
})(ActionDetails);
