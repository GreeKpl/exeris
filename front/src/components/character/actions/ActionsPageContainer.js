import {connect} from "react-redux";

import React from "react";
import {Grid, Row, Col, Panel, Tab, Tabs} from "react-bootstrap";
import ActionsFilterContainer from "./ActionsFilterContainer";
import ActionsListContainer from "./ActionsListContainer";
import ActionDetailsContainer from "./ActionDetailsContainer";

export class ActionsPage extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {

    if (this.props.isSmall) {
      return (
        <Tabs bsStyle="tabs" className="TupleNavTabsContainer" defaultActiveKey={1}>
          <Tab eventKey={1} title="List">
            <ActionsFilterContainer characterId={this.props.characterId}/>
            <ActionsListContainer characterId={this.props.characterId}/>
          </Tab>
          <Tab eventKey={2} title="Info">
            <Panel>
              <ActionDetailsContainer characterId={this.props.characterId}/>
            </Panel>
          </Tab>
        </Tabs>);
    } else {
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
}


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.params.characterId,
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
