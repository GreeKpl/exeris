import React from "react";
import {Panel, ListGroup, ListGroupItem} from "react-bootstrap";


const CharacterEntry = ({id, name}) => (
  <ListGroupItem dangerouslySetInnerHTML={{__html: name}}/>
);


class CharactersList extends React.Component {

  constructor(props) {
    super(props);
  }

  componentDidMount() {
    this.props.requestState();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.characterId !== this.props.characterId) {
      this.props.requestState();
    }
  }

  render() {
    return <Panel header="People around">
      <ListGroup fill>
        {this.props.charactersAround.map(this.createCharacterEntry)}
      </ListGroup>
    </Panel>;
  }

  createCharacterEntry(character) {
    return <CharacterEntry
      key={character.get("id")}
      id={character.get("id")}
      name={character.get("name")}
    />;
  }
}

export default CharactersList;
