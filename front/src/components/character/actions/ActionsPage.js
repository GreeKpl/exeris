import React from "react";
import {Grid, Row, Col, Panel} from "react-bootstrap";
import ActionsFilterContainer from "./ActionsFilterContainer";
import ActionsListContainer from "./ActionsListContainer";
import ActionDetailsContainer from "./ActionDetailsContainer";

class ActionsPage extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Grid fluid={true}>
        <Row>
          <Col xs={12} md={6}>
            <Panel header="Actions">
              <ActionsFilterContainer characterId={this.props.characterId}/>
              <ActionsListContainer characterId={this.props.characterId}/>
            </Panel>
          </Col>
          <Col xs={12} md={6}>
            <Panel header="Action info">
              <ActionDetailsContainer characterId={this.props.characterId}/>
            </Panel>
          </Col>
        </Row>
      </Grid>);
  }
}

export default ActionsPage;
