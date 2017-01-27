import React from "react";
import {Form, FormGroup, Col, FormControl, ControlLabel, Button, ListGroup, ListGroupItem} from "react-bootstrap";

class ActionDetails extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      amount: 1
    };

    this.onChange = this.onChange.bind(this);
    this.renderAdditionalFormInputs = this.renderAdditionalFormInputs.bind(this);
  }

  onChange(event) {
    const newAmount = event.target.value;
    this.setState({amount: newAmount});
  }

  renderAdditionalFormInputs() {
    let renderedFormInputs = [];
    for (let formInput of this.props.actionDetails.get("requiredFormInputs")) {
      if (formInput.get("type") == "AmountInput") {
        renderedFormInputs.push(
          <FormGroup key={"form-" + formInput.get("name")} controlId={"form-" + formInput.get("name")}>
            <Col componentClass={ControlLabel} sm={3}>
              {formInput.get("name")}
            </Col>
            <Col sm={9}>
              <FormControl type="text" placeholder="amount" value={this.state.amount} onChange={this.onChange}/>
            </Col>
          </FormGroup>
        );
      } else if (formInput.get("type") == "NameInput") {
        renderedFormInputs.push(
          <FormGroup key={"form-" + formInput.get("name")} controlId={"form-" + formInput.get("name")}>
            <Col componentClass={ControlLabel} sm={3}>
              {formInput.get("name")}
            </Col>
            <Col sm={9}>
              <FormControl type="text" placeholder="Enter name..." defaultValue=""/>
            </Col>
          </FormGroup>
        );
      } else if (formInput.get("type") == "WorkDaysInput") {
        renderedFormInputs.push(
          <FormGroup key={"form-" + formInput.get("name")} controlId={"form-" + formInput.get("name")}>
            <Col componentClass={ControlLabel} sm={3}>
              {formInput.get("name")}
            </Col>
            <Col sm={9}>
              <FormControl type="text" placeholder="workDays" value={this.state.amount} onChange={this.onChange}/>
            </Col>
          </FormGroup>
        );
      } else if (formInput.get("type") == "AnimalResourceLevel") {
        renderedFormInputs.push(
          <FormGroup key={"form-" + formInput.get("name")} controlId={"form-" + formInput.get("name")}>
            <Col componentClass={ControlLabel} sm={3}>
              Animal resource level
            </Col>
            <Col sm={9} componentClass={FormControl.Static}>
              <ListGroup>
                {formInput.get("args").get("resource_type")}
              </ListGroup>
            </Col>
          </FormGroup>);
      }
    }
    return renderedFormInputs;
  }

  render() {
    const actionDetails = this.props.actionDetails;

    if (actionDetails.size == 0) {
      return null;
    }

    return (
      <Form horizontal>
        {actionDetails.get("errorMessages").size > 0 &&
        <FormGroup key="errorMessages" controlId="errorMessages">
          <Col componentClass={ControlLabel} sm={3}>
            Errors
          </Col>
          <Col sm={9} componentClass={FormControl.Static}>
            <ListGroup>
              {actionDetails.get("errorMessages").map(message => <ListGroupItem
                key={message}>{message}</ListGroupItem>)}
            </ListGroup>
          </Col>
        </FormGroup>}
        <FormGroup key="actionName" controlId="actionName">
          <Col componentClass={ControlLabel} sm={3}>
            Name
          </Col>
          <Col sm={9} componentClass={FormControl.Static}>
            {actionDetails.get("name")}
          </Col>
        </FormGroup>
        {actionDetails.get("requiresSubject") &&
        <FormGroup key="activitySubject" controlId="activitySubject">
          <Col componentClass={ControlLabel} sm={3}>
            Subject of activity
          </Col>
          <Col sm={9}>
            <FormControl componentClass="select" placeholder="Select subject...">
              {actionDetails.get("subjects").map(subject =>
                <option value={subject.get("id")}>
                  {subject.get("name")}
                </option>)}
            </FormControl>
          </Col>
        </FormGroup>}
        {actionDetails.get("requiredInput").size > 0 &&
        <FormGroup key="requiredInput" controlId="requiredInput">
          <Col componentClass={ControlLabel} sm={3}>
            Required input
          </Col>
          <Col sm={9} componentClass={FormControl.Static}>
            <ListGroup>
              {actionDetails.get("requiredInput").map(input => <ListGroupItem key={input}>{input}</ListGroupItem>)}
            </ListGroup>
          </Col>
        </FormGroup>}
        {actionDetails.get("requiredTools").size > 0 &&
        <FormGroup key="requiredTools" controlId="requiredTools">
          <Col componentClass={ControlLabel} sm={3}>
            Required tools
          </Col>
          <Col sm={9} componentClass={FormControl.Static}>
            <ListGroup>
              {actionDetails.get("requiredTools").map(tool => <ListGroupItem key={tool}>{tool}</ListGroupItem>)}
            </ListGroup>
          </Col>
        </FormGroup>}
        {actionDetails.get("requiredMachines").size > 0 &&
        <FormGroup key="requiredMachines" controlId="requiredMachines">
          <Col componentClass={ControlLabel} sm={3}>
            Required machines
          </Col>
          <Col sm={9} componentClass={FormControl.Static}>
            <ListGroup>
              {actionDetails.get("requiredMachines").map(machine => <ListGroupItem
                key={machine}>{machine}</ListGroupItem>)}
            </ListGroup>
          </Col>
        </FormGroup>}
        <FormGroup key="requiredDays" controlId="requiredDays">
          <Col componentClass={ControlLabel} sm={3}>
            Required days
          </Col>
          <Col sm={9} componentClass={FormControl.Static}>
            {actionDetails.get("requiredDays") * this.state.amount} = {actionDetails.get("requiredDays")}
            {" "}
            x {this.state.amount}
          </Col>
        </FormGroup>
        {actionDetails.get("requiredSkills").size > 0 &&
        <FormGroup key="requiredSkill" controlId="requiredSkill">
          <Col componentClass={ControlLabel} sm={3}>
            Required skills
          </Col>
          <Col sm={9} componentClass={FormControl.Static}>
            <ListGroup>
              {actionDetails.get("requiredSkills").map(skill => <ListGroupItem key={skill}>{skill}</ListGroupItem>)}
            </ListGroup>
          </Col>
        </FormGroup>}
        {this.renderAdditionalFormInputs()}
        <FormGroup key="submit">
          <Col smOffset={3} sm={9}>
            <Button type="submit" disabled={actionDetails.get("errorMessages").size > 0}>
              Start an activity
            </Button>
          </Col>
        </FormGroup>
      </Form>);
  }
}

export default ActionDetails;
