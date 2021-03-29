import Rete from 'rete'
import { strSocket } from '../sockets.js'
import InputControl from '../controls/input'

class ReteEnd extends Rete.Component {
  constructor () {
    super('End')
  }

  builder (node) {
    const input = new Rete.Input('input', 'String', strSocket, true)
    const output = new Rete.Output('output', 'String', strSocket, true)
    return node.addInput(input)
      .addControl(new InputControl('end', this.editor, ''))
      .addOutput(output)
  }
}

export default ReteEnd
