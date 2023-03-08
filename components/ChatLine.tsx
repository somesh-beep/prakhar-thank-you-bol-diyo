import clsx from 'clsx'
import Balancer from 'react-wrap-balancer'
import Source from "../components/Source";
import { AuthorDetails } from '../pages';
import { HiShieldExclamation } from 'react-icons/hi';

const BalancerWrapper = (props: any) => <Balancer {...props} />

export type Message = {
  who: 'bot' | 'user' | undefined
  message?: string
  sources?: any
  authorDetails?: AuthorDetails,
  isPlausible?: boolean,
}

// loading placeholder animation for the chat line
export const LoadingChatLine = () => (
  <div className="flex min-w-full animate-pulse px-4 py-5 sm:px-6">
    <div className="flex flex-grow space-x-3">
      <div className="min-w-0 flex-1">
        <p className="font-large text-xxl text-gray-900">
          <a href="#" className="hover:underline">
            AI
          </a>
        </p>
        <div className="space-y-4 pt-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="col-span-2 h-2 rounded bg-zinc-500"></div>
            <div className="col-span-1 h-2 rounded bg-zinc-500"></div>
          </div>
          <div className="h-2 rounded bg-zinc-500"></div>
        </div>
      </div>
    </div>
  </div>
)

// util helper to convert new lines to <br /> tags
const convertNewLines = (text: string) =>
  text.split('\n').map((line, i) => (
    <span key={i}>
      {line}
      <br />
    </span>
  ))

export function ChatLine({ who = 'bot', message, sources, authorDetails, isPlausible}: Message) {
  if (!message) {
    return null
  }
  const formatteMessage = convertNewLines(message)
  return (
    <div
      className={
        who != 'bot' ? 'float-right clear-both' : 'float-left clear-both'
      }
    >
      <BalancerWrapper>
        <div className="float-right mb-5 rounded-lg bg-white px-4 py-5 shadow-lg ring-1 ring-zinc-100 sm:px-6">
          <div className="flex space-x-3">
            <div className="flex-1 gap-4 flex flex-row">
            

{who == 'bot' && <div className="flex-shrink-0" hidden={authorDetails === undefined}>
    <img className="w-10 h-10 rounded-full" src={authorDetails?.authorImageUrl} alt=""/>
    <span className="top-0 left-7 absolute  w-3.5 h-3.5 bg-green-400 border-2 border-white dark:border-gray-800 rounded-full"></span>
</div>
}

              <div>
              <p className="font-large text-xxl text-gray-900">
                <a href="#" className="hover:underline">
                  {who == 'bot' ? authorDetails?.authorName || 'AI' : 'You'}
                </a>
              </p>
              {isPlausible === false && (

<div className="flex flex-row items-center text-orange-600 mb-6">
<HiShieldExclamation className="mr-2 h-5 w-5" />This answer might be incorrect given the sources.
</div>


              )}
              <p
                className={clsx(
                  'text ',
                  who == 'bot' ? 'font-semibold font- ' : 'text-gray-400'
                )}
              >
                {formatteMessage}
                    
               
              </p>
              {sources && sources.map((source_doc, index) => {
                              const {page_content, metadata} = source_doc
                              const {page, source} = metadata
                              return (
                                   <Source key={index} index={index+1} page={page} page_content={page_content} source={source} />
                              )
                        })}
            </div>
            </div>
          </div>
        </div>
      </BalancerWrapper>
    </div>
  )
}
