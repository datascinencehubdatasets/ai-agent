// Simple tests using node-fetch mocking are not set up in this repo;
// provide guidance and example jest tests instead.

// Example Jest test (place in frontend tests if jest configured):
/*
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { renderHook, act } from '@testing-library/react-hooks';
import { useChat } from '@/hooks/useChat';

const server = setupServer(
  rest.post('http://127.0.0.1:8000/route', (req, res, ctx) => {
    return res(ctx.json({ intent: 'test', confidence: 0.9, agent: 'general', answer: 'ok', extra: {} }));
  }),
  rest.post('http://127.0.0.1:8000/intent/classify', (req, res, ctx) => {
    return res(ctx.json({ intent: 'product_recommendation', confidence: 0.95 }));
  })
);

describe('useChat', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  it('sends a message and receives answer', async () => {
    const { result } = renderHook(() => useChat('ru'));
    await act(async () => result.current.setInputValue('hello'));
    await act(async () => result.current.send());
    expect(result.current.messages.length).toBeGreaterThan(1);
  });

  it('classifyIntent returns intent without adding to messages', async () => {
    const { result } = renderHook(() => useChat('ru'));
    await act(async () => result.current.setInputValue('что такое мурaбаха?'));
    const res = await result.current.classifyIntent();
    expect(res.intent).toBe('product_recommendation');
    expect(result.current.messages.length).toBe(0);
  });
});
*/
