import Rete from 'rete'
import { strSocket } from '../sockets.js'
import 'codemirror/mode/javascript/javascript.js'
import InputControl from '../controls/input'
import RadioControl from '../controls/radio'
import TextAreaControl from '../controls/text-area'

class ReteDialogue extends Rete.Component {
  constructor () {
    super('Dialogue')
  }

  builder (node) {
    var input = new Rete.Input('input', 'String', strSocket, true)
    var output = new Rete.Output('output', 'String', strSocket, true)
    var controls = {
      'name': new InputControl('name', this.editor, 'dialogue'),
      'question': new InputControl('question', this.editor, 'utterance'),
      'pretext': new TextAreaControl('pretext', this.editor, 'pretext'),
      'context_var': new InputControl('context_var', this.editor, 'context variable'),
      'context_var_mode': new RadioControl('context_var_mode', this.editor, ''),
      'transition': new InputControl('transition', this.editor, 'transition'),
      'pretext2': new InputControl('pretext2', this.editor, 'pretext for templated answer'),
      'template': new InputControl('template', this.editor, 'template'),
      'data': new TextAreaControl('data', this.editor, 'additional answer')
    }

    node.addInput(input).addOutput(output)
    for (var key in controls) {
      node.addControl(controls[key])
    }

    return node
  }
}

export default ReteDialogue
