import {connect} from "react-redux";
import React from "react";
import {Grid, Row, Col, Tab, Tabs} from "react-bootstrap";
import EventsListContainer from "./EventsListContainer";
import CharactersListContainer from "./CharactersListContainer";
import SpeechPanelContainer from "./SpeechPanelContainer";
import TopPanelContainer from "../topPanel/TopPanelContainer";
import "./style.scss";

export class EventsPage extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    if (this.props.isSmall) {
      return (
        <Tabs bsStyle="tabs" className="TupleNavTabsContainer" defaultActiveKey={1}>
          <Tab eventKey={1} title="Speaking">
            <SpeechPanelContainer characterId={this.props.characterId}/>
            <EventsListContainer characterId={this.props.characterId}/>
          </Tab>
          <Tab eventKey={2} title="People">
            <TopPanelContainer characterId={this.props.characterId}/>
            <CharactersListContainer characterId={this.props.characterId}/>
          </Tab>
        </Tabs>);
    } else {
      return (
        <Grid fluid={true}>
          <Row>
            <Col xs={12} md={8}>
              <TopPanelContainer characterId={this.props.characterId}/>
              <SpeechPanelContainer characterId={this.props.characterId}/>
              <EventsListContainer characterId={this.props.characterId}/>
            </Col>
            <Col xs={12} md={4}>
              <CharactersListContainer characterId={this.props.characterId}/>
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

const EventsPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(EventsPage);

export default EventsPageContainer;
