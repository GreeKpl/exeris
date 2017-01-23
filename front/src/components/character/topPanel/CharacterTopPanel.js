import React from "react";
import {
  Panel,
  Grid,
  Row,
  ListGroupItem,
  Col,
  Glyphicon,
  ControlLabel,
  Form,
  FormGroup,
  FormControl,
} from "react-bootstrap";

class CharacterTopPanel extends React.Component {
  constructor(props) {
    super(props);
  }


  render() {
    return <Panel header="Character info">
      <Grid fluid>
        <Row>
          <Col xs={12} md={3}>
            <Form horizontal>
              <FormGroup controlId="characterName">
                <Col componentClass={ControlLabel} sm={4}>
                  Name
                </Col>
                <Col componentClass={FormControl.Static} sm={8}>
                  {this.props.name} <Glyphicon glyph="pencil"/>
                </Col>
              </FormGroup>
              <FormGroup controlId="characterName">
                <Col componentClass={ControlLabel} sm={4}>
                  Location
                </Col>
                <Col componentClass={FormControl.Static} sm={8}>
                  {this.props.locationName} <Glyphicon glyph="globe"/>
                </Col>
              </FormGroup>
              {this.props.workIntent &&
              <FormGroup controlId="characterName">
                <Col componentClass={ControlLabel} sm={4}>
                  Working on
                </Col>
                <Col componentClass={FormControl.Static} sm={8}>
                  {this.props.workIntent}
                </Col>
              </FormGroup>}
              {this.props.combatIntent &&
              <FormGroup controlId="characterName">
                <Col componentClass={ControlLabel} sm={4}>
                  Fighting in
                </Col>
                <Col componentClass={FormControl.Static} sm={8}>
                  {this.props.combatIntent}
                </Col>
              </FormGroup>}
            </Form>
          </Col>
          <Col xs={12} md={3}>
            <FormGroup controlId="inventory">
              <ControlLabel>Equipment</ControlLabel>
              <FormControl componentClass="list-group">
                {this.props.equipment.map(itemName => <ListGroupItem>{itemName}</ListGroupItem>)}
              </FormControl>
            </FormGroup>
          </Col>
          <Col xs={12} md={6}>
            <Form horizontal>
              <FormGroup controlId="shortDescription">
                <Col componentClass={ControlLabel} sm={3}>
                  Short description
                </Col>
                <Col componentClass={FormControl.Static} sm={9}>
                  {this.props.shortDescription}
                </Col>
              </FormGroup>
              <FormGroup controlId="longDescription">
                <Col componentClass={ControlLabel} sm={3}>
                  Long description
                </Col>
                <Col componentClass={FormControl.Static} sm={9}>
                  {this.props.longDescription}
                </Col>
              </FormGroup>
            </Form>
          </Col>
        </Row>
      </Grid>
    </Panel>;
  }
}


export default CharacterTopPanel;
