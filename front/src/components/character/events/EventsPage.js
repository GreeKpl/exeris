import React from "react";
import {Grid, Row, Col} from "react-bootstrap";
import EventsListContainer from "./EventsListContainer";
import CharactersListContainer from "./CharactersListContainer";
import SpeakPanelContainer from "./SpeakPanelContainer";

class EventsPage extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Grid fluid={true}>
        <Row>
          <Col xs={12} md={8}>
            <SpeakPanelContainer characterId={this.props.characterId}/>
            <EventsListContainer characterId={this.props.characterId}/>
          </Col>
          <Col xs={12} md={4}>
            <CharactersListContainer characterId={this.props.characterId}/>
          </Col>
        </Row>
      </Grid>);
  }
}

export default EventsPage;
