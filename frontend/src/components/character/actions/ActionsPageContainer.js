import {connect} from "react-redux";

import React from "react";
import {Card, Col, Container, Row, Tab, Tabs} from "react-bootstrap";
import ActionsFilterContainer from "./ActionsFilterContainer";
import ActionsListContainer from "./ActionsListContainer";
import ActionDetailsContainer from "./ActionDetailsContainer";

export class ActionsPage extends React.Component {
  render() {

    if (this.props.isSmall) {
      return (
        <Tabs variant="tabs" className="TupleNavTabsContainer" defaultActiveKey={1}>
          <Tab eventKey={1} title="List">
            <ActionsFilterContainer characterId={this.props.characterId}/>
            <ActionsListContainer characterId={this.props.characterId}/>
          </Tab>
          <Tab eventKey={2} title="Info">
            <Card>
              <Card.Body>
                <ActionDetailsContainer characterId={this.props.characterId}/>
              </Card.Body>
            </Card>
          </Tab>
        </Tabs>);
    } else {
      return (
        <Container fluid={true}>
          <Row>
            <Col xs={12} md={6}>
              <Card>
                <Card.Header>Actions</Card.Header>
                <Card.Body>
                  <ActionsFilterContainer characterId={this.props.characterId}/>
                  <ActionsListContainer characterId={this.props.characterId}/>
                </Card.Body>
              </Card>
            </Col>
            <Col xs={12} md={6}>
              <Card>
                <Card.Header>Action info</Card.Header>
                <Card.Body>
                  <ActionDetailsContainer characterId={this.props.characterId}/>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      );
    }
  }
}


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.match.params.characterId,
    isSmall: state.get("browser").atMost.small,
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const ActionsPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ActionsPage);

export default ActionsPageContainer;
