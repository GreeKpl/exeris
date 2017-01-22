import React from "react";
import {Grid, Row, Col} from "react-bootstrap";
import EventsListContainer from "./EventsListContainer";
import CharactersListContainer from "./CharactersListContainer";
import SpeechPanelContainer from "./SpeechPanelContainer";

class EventsPage extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Grid fluid={true}>
        <Row>
          <Col xs={12} md={8}>
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

export default EventsPage;
