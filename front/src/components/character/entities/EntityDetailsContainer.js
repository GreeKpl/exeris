import {connect} from "react-redux";
import {fromEntitiesState, getSelectedDetails, updateExpandedInput} from "../../../modules/entities";
import {performAddEntityToItemAction} from "../../../modules/entities-actionsAddon";

import React from "react";
import {Button, Card, Col, Container, Form, ListGroup, ListGroupItem, Row} from "react-bootstrap";


const OptionalCol = ({value, children}) => {
  if (value) {
    return <Col>{children}</Col>
  } else {
    return null;
  }
};

export class EntityDetails extends React.Component {
  render() {
    return (
      <Card>
        <Card.Header>EntityInfo</Card.Header>
        <Card.Body>
          <Container>
            <Row>
              <Col>Type: {this.props.details.get("type")}</Col>
              <Col>Name: {this.props.details.get("name")}</Col>
            </Row>
          </Container>
        </Card.Body>
      </Card>);
  }
}

class AddInputSelection extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      amount: 0,
      selectedItem: "",
    };

    this.handleAmountChange = this.handleAmountChange.bind(this);
    this.handleSelectChange = this.handleSelectChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleAmountChange(event) {
    const value = event.target.value;
    this.setState({
      amount: value,
      selectedItem: this.state.selectedItem
    });
  }

  handleSelectChange(event) {
    this.setState({
      amount: this.state.amount,
      selectedItem: event.target.value
    });
  }

  handleSubmit() {
    this.props.onSubmitForm(this.props.activityId, this.props.expandedInput,
      this.state.selectedItem, +this.state.amount);
  }

  render() {
    const expandedDetails = this.props.expandedDetails;
    return <Form autoComplete="off">
      <Form.Group controlId="addToActivitySelect">
        <Form.Label>Select resource to add:</Form.Label>
        <Form.Control
          value={this.state.selectedItem}
          componentClass="select"
          onChange={this.handleSelectChange}
          placeholder="select">
          {expandedDetails && expandedDetails.get("itemsToAdd").map(item => <option
            value={item.get("id")}>{item.get("name")}</option>)}
        </Form.Control>
      </Form.Group>
      <Form.Group controlId="addToActivityAmount">
        <Form.Label>Amount</Form.Label>
        <Form.Control
          type="text"
          placeholder="Amount"
          value={this.state.amount}
          onChange={this.handleAmountChange}/>
      </Form.Group>
      <Button onClick={this.handleSubmit}>Confirm</Button>
    </Form>;
  }
}


export class InputRequirement extends React.Component {

  constructor(props) {
    super(props);

    this.handleExpand = this.handleExpand.bind(this);
    this.handleCollapse = this.handleCollapse.bind(this);
  }

  render() {
    const {name, itemData, expanded, expandedInput, expandedDetails, activityId, onSubmitForm} = this.props;
    return <ListGroupItem>
      {name} - {itemData.get("needed") - itemData.get("left")} / {itemData.get("needed")}
      {expanded ? [
          <Button key="button-collapse" onClick={this.handleCollapse}>Hide</Button>,
          <AddInputSelection
            key="add-input-selection"
            activityId={activityId}
            expandedInput={expandedInput}
            expandedDetails={expandedDetails}
            onSubmitForm={onSubmitForm}/>]
        : <Button onClick={this.handleExpand}>Add stuff</Button>}
    </ListGroupItem>;
  }

  handleExpand() {
    this.props.onExpandInput(this.props.name);
  }

  handleCollapse() {
    this.props.onCollapseInput();
  }
}

const InputRequirements = ({
                             reqInputs, expandedInput, expandedInputDetails, activityId,
                             onExpandInput, onCollapseInput, onSubmitForm
                           }) =>
  <ListGroup>
    {reqInputs.map((input, name) => <InputRequirement
      name={name}
      itemData={input}
      expanded={expandedInput === name}
      expandedInput={expandedInput}
      expandedDetails={expandedInputDetails}
      activityId={activityId}
      onExpandInput={onExpandInput}
      onCollapseInput={onCollapseInput}
      onSubmitForm={onSubmitForm}
      key={name}
    />).valueSeq()}
  </ListGroup>;

export class ActivityDetails extends React.Component {

  render() {
    const {details, onExpandInput, onCollapseInput, onSubmitForm} = this.props;
    return (
      <Card>
        <Card.Header>ActivityInfo</Card.Header>
        <Card.Body>
          <Container fluid={true}>
            <Row>
              <Col>Name: {details.get("name")}</Col>
              {details.has("input") &&
              <OptionalCol value={details.get("input")}>
                <InputRequirements
                  activityId={details.get("id")}
                  reqInputs={details.get("input")}
                  expandedInput={details.get("expandedInput")}
                  expandedInputDetails={details.get("expandedInputDetails")}
                  onExpandInput={onExpandInput}
                  onCollapseInput={onCollapseInput}
                  onSubmitForm={onSubmitForm}/>
              </OptionalCol>}
              <Col>Work left: {details.get("ticksLeft")} / {details.get("ticksNeeded")}</Col>
            </Row>
          </Container>
        </Card.Body>
      </Card>
    );
  }
}


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    details: getSelectedDetails(fromEntitiesState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

export const EntityDetailsContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(EntityDetails);


export const ActivityDetailsContainer = connect(
  mapStateToProps,
  (dispatch, ownProps) => {
    return {
      onSubmitForm: (activityId, reqGroup, addedItemId, amount) => {
        dispatch(performAddEntityToItemAction(ownProps.characterId,
          activityId, reqGroup, addedItemId, amount));
      },
      onExpandInput: inputName => {
        dispatch(updateExpandedInput(ownProps.characterId, inputName));
      },
      onCollapseInput: () => {
        dispatch(updateExpandedInput(ownProps.characterId, null));
      }
    }
  }
)(ActivityDetails);
