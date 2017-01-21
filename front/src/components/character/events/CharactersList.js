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
    this.props.onMount();
  }

  render() {
    return <Panel header="People around">
      <ListGroup fill>
        {this.props.charactersAround.map(character => (
          <CharacterEntry
            key={character.get("id")}
            id={character.get("id")}
            name={character.get("name")}
          />
        ))}
      </ListGroup>
    </Panel>;
  }
}

export default CharactersList;
