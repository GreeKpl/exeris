import React from "react";
import {Grid, Row, Col, Panel, ListGroup, ListGroupItem, Button} from "react-bootstrap";


const OptionalCol = ({value, children}) => {
  if (value) {
    return <Col>{children}</Col>
  } else {
    return null;
  }
};

export class EntityDetails extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Panel header="EntityInfo">
        <Grid>
          <Row>
            <Col>Type: {this.props.details.get("type")}</Col>
            <Col>Name: {this.props.details.get("name")}</Col>
          </Row>
        </Grid>
      </Panel>);
  }
}


const InputRequirement = ({name, itemData}) =>
  <ListGroupItem>
    {name} {itemData.get("needed") - itemData.get("left")} / {itemData.get("needed")}
    <Button>Add stuff</Button>
  </ListGroupItem>;

const InputRequirements = ({reqInputs}) =>
  <ListGroup>
    {reqInputs.map((input, name) => <InputRequirement name={name} itemData={input}/>)}
  </ListGroup>;

export class ActivityDetails extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    const details = this.props.details;
    return (
      <Panel header="ActivityInfo">
        <Grid>
          <Row>
            <Col>Name: {details.get("name")}</Col>
            {details.has("input") &&
            <OptionalCol value={details.get("input")}>
              <InputRequirements reqInputs={details.get("input")}/>
            </OptionalCol>}
            <Col>Work left: {details.get("ticksLeft")} / {details.get("ticksNeeded")}</Col>
          </Row>
        </Grid>
      </Panel>);
  }
}
