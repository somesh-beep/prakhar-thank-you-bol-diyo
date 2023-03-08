import { Layout, Text, Page } from '@vercel/examples-ui'
import { Chat } from '../components/Chat'
import { useRouter } from 'next/router'
import Documents from "../components/Documents";
import { useState } from "react";

export type AuthorDetails = {
  authorName: string,
  authorImageUrl: string,
}

function Home() {
  const {query, isReady} = useRouter()
  const [authorDetails, setAuthorDetails] = useState<AuthorDetails|undefined>(undefined);

  const fetchAuthorDetails = async (authorId) => {
    const response = await fetch('/api/author', {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
        body: JSON.stringify({
          authorId: authorId,
        }),
  
    });
  
    const {authorDetails} = await response.json();
    setAuthorDetails(authorDetails)
  };
  let {dbId, authorId} = query
  dbId = dbId as string || process.env.NEXT_PUBLIC_INDEX_NAME as string;

  if (authorId){
      dbId=authorId as string
      if (!authorDetails){
        fetchAuthorDetails(authorId)
      }
  }


  const errorMessage = (
        <div className="rounded-md bg-red-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p>Unknown index selected.</p>
              </div>
            </div>
          </div>
          )

  return (
    <Page className="flex flex-col gap-12">
      <section className="flex flex-col gap-6">
        {authorDetails ? 
        (<Text variant="h1">Chat with <span className="text-transparent bg-clip-text bg-gradient-to-r to-emerald-600 from-sky-400">{authorDetails.authorName}</span></Text>) : 
        (<Text variant="h1">Chat with your books 🧠</Text>)}
        {isReady ? <Documents dbId={dbId}/>: <div/>}
      </section>

      <section className="flex flex-col gap-3">
        <div className="lg">
            { typeof dbId == "undefined" && errorMessage}
             <Chat dbId={dbId as string} authorDetails={authorDetails}/>
        </div>
      </section>
    </Page>
  )
}

Home.Layout = Layout

export default Home
